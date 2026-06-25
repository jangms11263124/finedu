"""AI 콘텐츠 추천 (2단계 RAG 파이프라인).

구성:
  [1단계 · Retrieval] Gemini 임베딩으로 콘텐츠/사용자 신호를 벡터화하고
    코사인 유사도로 관련 콘텐츠 후보 10~20개를 빠르고 저렴하게 추린다.
  [2단계 · Generation] GPT-4o-mini가 후보 메타데이터를 받아 사용자 취향에
    맞게 3~4개씩 '번들'로 묶고 스토리라인(추천 사유)을 생성한다.
    Structured Outputs(JSON Schema)로 UI에 바로 쓸 수 있는 JSON을 받는다.

두 모델 모두 SSAFY GMS 게이트웨이를 경유한다. GMS는 실제 공급자 엔드포인트
앞에 https://gms.ssafy.io/gmsapi/ 를 붙이고 쿼리스트링 ?key=$GMS_KEY 로
인증하므로, 공식 SDK 대신 httpx로 REST를 직접 호출한다.

GMS_KEY 가 없거나 오류가 나면 규칙 기반 추천(번들 형태)으로 자동 대체한다.
"""
import hashlib
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count

from .models import Content

logger = logging.getLogger(__name__)

# 검색 단계에서 추려낼 후보 수 (LLM에 넘길 만큼만 여유 있게)
RETRIEVE_K = 18
# 코퍼스 상한 (임베딩 비용 제어)
CORPUS_SIZE = 60

# 2단계 구조화 출력 스키마 — 번들(묶음) 단위 추천
_OUTPUT_SCHEMA = {
    'type': 'object',
    'properties': {
        'summary': {'type': 'string'},
        'bundles': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'storyline': {'type': 'string'},
                    'content_ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                    },
                },
                'required': ['title', 'storyline', 'content_ids'],
            },
        },
    },
    'required': ['summary', 'bundles'],
}


# ---------------------------------------------------------------------------
# 코퍼스 · 사용자 신호
# ---------------------------------------------------------------------------
def _corpus(exclude_ids=None):
    """추천 후보 콘텐츠 코퍼스. exclude_ids 는 추천에서 제외할 콘텐츠 id."""
    qs = Content.objects.annotate(_likes=Count('likes'))
    if exclude_ids:
        qs = qs.exclude(id__in=exclude_ids)
    qs = qs.order_by('-views')[:CORPUS_SIZE]
    return [
        {
            'id': c.id,
            'title': c.title,
            'summary': c.summary,
            'body': c.body,
            'category': c.get_category_display(),
            'views': c.views,
            'likes': c._likes,
        }
        for c in qs
    ]


def _attendance_streak(user):
    """오늘(또는 어제)부터 거슬러 연속 출석한 일수."""
    from datetime import date, timedelta

    dates = set(user.attendances.values_list('date', flat=True))
    if not dates:
        return 0
    today = date.today()
    cur = today if today in dates else today - timedelta(days=1)
    streak = 0
    while cur in dates:
        streak += 1
        cur -= timedelta(days=1)
    return streak


def _user_signals(user, ebti):
    """사용자 맞춤 신호."""
    is_auth = user and user.is_authenticated

    liked_ids, liked_cats, liked_titles = [], [], []
    community = []
    quiz_weak = []
    streak = 0

    if is_auth:
        # 좋아요한 콘텐츠 (카테고리·제목·id)
        liked_qs = user.liked_contents.all()
        liked_ids = list(liked_qs.values_list('id', flat=True))
        liked_cats = list(liked_qs.values_list('category', flat=True))
        liked_titles = list(
            liked_qs.order_by('-id').values_list('title', flat=True)[:8]
        )

        # 커뮤니티 관심 주제: 작성 글 + 댓글 단 콘텐츠 + 좋아요한 글
        community = list(user.posts.values_list('title', flat=True)[:6])
        community += list(
            user.content_comments.values_list('content__title', flat=True)[:5]
        )
        community += list(user.liked_posts.values_list('title', flat=True)[:5])
        community = list(dict.fromkeys(t for t in community if t))  # 중복·빈값 제거

        # 최근 틀린 퀴즈 (문제+해설) — 보완이 필요한 약점 신호
        wrong = (
            user.quiz_attempts.filter(is_correct=False)
            .select_related('quiz')
            .order_by('-created_at')[:5]
        )
        quiz_weak = [
            f'{a.quiz.question} (해설: {a.quiz.explanation})'
            if a.quiz.explanation else a.quiz.question
            for a in wrong
        ]

        # 학습 몰입도 (연속 출석)
        streak = _attendance_streak(user)

    # 프론트에서 전달된 ebti가 없으면 DB에 저장된 값 사용
    resolved_ebti = ebti or (getattr(user, 'ebti_result', None) if is_auth else None)

    top = (
        Content.objects.values('category')
        .annotate(v=Count('id'))
        .order_by('-v')[:3]
    )
    return {
        'ebti': resolved_ebti,
        'liked_categories': liked_cats,
        'liked_titles': liked_titles,
        'liked_ids': liked_ids,
        'community_posts': community,
        'trending_topics': [t['category'] for t in top],
        'quiz_weak': quiz_weak,
        'streak': streak,
    }


def recommend(user, ebti=None, limit=12):
    """추천 결과 dict 반환.

    {summary, bundles:[{title, storyline, items:[{content, reason}]}],
     items:[{content, reason}], source, signals_meta}
    items 는 번들을 평면화한 호환용 필드.
    signals_meta 는 각 신호의 실제 존재 여부 (프론트 칩 표시용).
    """
    signals = _user_signals(user, ebti)
    # 이미 좋아요한 콘텐츠는 추천에서 제외 → 새로운 발견을 늘린다
    corpus = _corpus(exclude_ids=signals.get('liked_ids'))

    signals_meta = {
        'has_ebti': bool(signals.get('ebti')),
        'has_liked_contents': bool(signals.get('liked_categories')),
        'has_community': bool(signals.get('community_posts')),
        'has_trending': bool(signals.get('trending_topics')),
        'has_quiz_weak': bool(signals.get('quiz_weak')),
        'has_streak': bool(signals.get('streak')),
    }

    if settings.GMS_KEY:
        try:
            candidates = _retrieve(corpus, signals, RETRIEVE_K)
            result = _generate(candidates, signals, limit)
            result['signals_meta'] = signals_meta
            return result
        except Exception as exc:
            logger.warning('AI 추천 실패, 규칙 기반으로 대체: %s', exc)

    result = _rule_recommend(corpus, signals, limit)
    result['signals_meta'] = signals_meta
    return result


# ---------------------------------------------------------------------------
# 1단계 · Retrieval (Gemini 임베딩 + 코사인 유사도)
# ---------------------------------------------------------------------------
def _content_text(c):
    """임베딩에 쓸 콘텐츠 텍스트 (본문은 길이 제한)."""
    body = (c.get('body') or '')[:1500]
    return f"제목: {c['title']}\n분류: {c['category']}\n요약: {c['summary']}\n본문: {body}"


def _query_text(signals):
    """사용자 신호를 검색 쿼리 텍스트로 변환."""
    ebti = signals.get('ebti') or {}
    weak = []
    for b in (ebti.get('breakdown') or []):
        if not b.get('strong'):
            weak += b.get('tags', [])
    parts = [
        f"관심 카테고리: {', '.join(signals['liked_categories']) or '없음'}",
        f"좋아한 콘텐츠: {', '.join(signals.get('liked_titles') or []) or '없음'}",
        f"커뮤니티 관심 주제: {', '.join(signals['community_posts']) or '없음'}",
        f"최근 인기 주제: {', '.join(signals['trending_topics']) or '없음'}",
        f"보완하면 좋은 영역(EBTI): {', '.join(weak) or '없음'}",
        f"최근 틀린 퀴즈 주제: {' / '.join(signals.get('quiz_weak') or []) or '없음'}",
    ]
    return '\n'.join(parts)


def _embed(texts):
    """OpenAI 임베딩(GMS 경유) — 텍스트 리스트 → 벡터 리스트(list[list[float]]).

    GMS 패턴: api.openai.com 앞에 GMS prefix를 붙이고
    Authorization: Bearer $GMS_KEY 헤더로 인증한다.
    """
    import httpx

    url = f'{settings.GMS_BASE_URL}/api.openai.com/v1/embeddings'
    payload = {
        'model': 'text-embedding-3-small',
        'input': texts,
    }
    resp = httpx.post(
        url,
        headers={'Authorization': f'Bearer {settings.GMS_KEY}'},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    items = sorted(resp.json()['data'], key=lambda x: x['index'])
    return [item['embedding'] for item in items]


def _embed_corpus(corpus):
    """코퍼스 임베딩 (콘텐츠별로 캐싱해 재호출 비용 절감)."""
    vectors = [None] * len(corpus)
    misses = []  # (index, cache_key, text)
    for i, c in enumerate(corpus):
        text = _content_text(c)
        digest = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
        key = f"emb:text-embedding-3-small:{c['id']}:{digest}"
        cached = cache.get(key)
        if cached is not None:
            vectors[i] = cached
        else:
            misses.append((i, key, text))

    if misses:
        fresh = _embed([m[2] for m in misses])
        for (i, key, _), vec in zip(misses, fresh):
            vectors[i] = vec
            cache.set(key, vec, 60 * 60 * 24 * 7)  # 7일 캐시
    return vectors


def _retrieve(corpus, signals, k):
    """코사인 유사도 상위 k개 후보 반환."""
    import numpy as np

    if not corpus:
        return []

    doc_vecs = np.array(_embed_corpus(corpus), dtype=np.float32)
    query_vec = np.array(_embed([_query_text(signals)])[0], dtype=np.float32)

    # 정규화 후 내적 = 코사인 유사도
    doc_norm = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-9)
    q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    sims = doc_norm @ q_norm

    top_idx = np.argsort(sims)[::-1][:k]
    return [corpus[i] for i in top_idx]


# ---------------------------------------------------------------------------
# 2단계 · Generation (GPT-4o-mini Structured Outputs)
# ---------------------------------------------------------------------------
def _generate(candidates, signals, limit):
    import httpx

    # LLM에는 본문 대신 메타데이터만 (토큰 절약)
    meta = [
        {
            'id': c['id'],
            'title': c['title'],
            'summary': c['summary'],
            'category': c['category'],
            'views': c['views'],
            'likes': c['likes'],
        }
        for c in candidates
    ]

    # 프롬프트에 넣을 사용자 신호 요약 (빈 값 제외)
    liked = signals.get('liked_categories') or []
    posts = signals.get('community_posts') or []
    quiz_weak = signals.get('quiz_weak') or []
    streak = signals.get('streak') or 0
    ebti = signals.get('ebti') or {}
    weak_areas = [
        b['name'] for b in (ebti.get('breakdown') or []) if not b.get('strong')
    ]
    strong_areas = [
        b['name'] for b in (ebti.get('breakdown') or []) if b.get('strong')
    ]

    signal_lines = []
    if liked:
        signal_lines.append(f'- 관심 콘텐츠 카테고리: {", ".join(set(liked))}')
    if posts:
        signal_lines.append(f'- 커뮤니티 관심 주제(글·댓글·좋아요): {", ".join(posts[:5])}')
    if strong_areas:
        signal_lines.append(f'- EBTI 강점 영역: {", ".join(strong_areas)}')
    if weak_areas:
        signal_lines.append(f'- EBTI 보완 영역: {", ".join(weak_areas)}')
    if quiz_weak:
        signal_lines.append(f'- 최근 퀴즈에서 틀린 주제(보완 필요): {" / ".join(quiz_weak[:3])}')
    if streak:
        signal_lines.append(f'- 학습 몰입도: 연속 출석 {streak}일')
    signal_summary = '\n'.join(signal_lines) if signal_lines else '- (신규 사용자, 데이터 없음)'

    system = (
        '당신은 금융 교육 플랫폼 im fine edu의 따뜻하고 친근한 AI 큐레이터입니다.\n'
        '아래 두 가지를 JSON으로 응답하세요.\n\n'
        '[1] summary (문자열)\n'
        '사용자 데이터를 분석했다는 느낌이 들도록, 실제 관심사·커뮤니티 활동·EBTI 결과·'
        '퀴즈 약점을 구체적으로 언급하며 2~3문장으로 작성하세요. '
        '예) "투자와 소비 분야 콘텐츠를 즐겨 보시고, 커뮤니티에서도 재테크 관련 글을 쓰셨네요! '
        '퀴즈에서 자주 틀린 예금자보호 쪽을 보완할 콘텐츠도 함께 담았어요." '
        '신규 사용자처럼 데이터가 없으면 "아직 활동 기록이 많지 않지만, 인기 콘텐츠를 중심으로 '
        '골라봤어요!" 처럼 자연스럽게 안내하세요. 절대 빈 데이터를 있는 것처럼 꾸미지 마세요.\n\n'
        '[2] bundles (배열)\n'
        '후보 콘텐츠(candidates) 안에서만 골라 3~4개씩 번들로 구성하세요. '
        '각 번들은 하나의 학습 흐름이 되도록 묶고, storyline 에는 이 묶음을 추천하는 이유를 '
        '한국어로 친근하게 2~3문장으로 적으세요. '
        '특히 "최근 퀴즈에서 틀린 주제"가 있으면 이를 보완하는 콘텐츠를 우선 포함하고 그 이유를 '
        'storyline 에 자연스럽게 녹이세요. '
        '"연속 출석" 일수가 길면(예: 7일 이상) 심화 콘텐츠를, 짧거나 없으면 입문 콘텐츠를 '
        '우선해 난이도를 맞추세요. '
        'title 은 번들을 대표하는 짧은 제목입니다. candidates 에 없는 id 는 절대 쓰지 마세요.'
    )
    user_msg = (
        f'## 분석된 사용자 신호\n{signal_summary}\n\n'
        f'## 전체 사용자 신호 (상세)\n{json.dumps(signals, ensure_ascii=False)}\n\n'
        f'## 후보 콘텐츠(candidates)\n{json.dumps(meta, ensure_ascii=False)}\n\n'
        f'위 사용자에게 맞춰 번들 3~4개를 만들어주세요. 번들당 콘텐츠는 3~4개, '
        f'전체 콘텐츠는 최대 {limit}개 이내로 하세요.'
    )

    # GMS 패턴: generativelanguage.googleapis.com 앞에 GMS prefix, ?key=$GMS_KEY 로 인증
    url = (
        f'{settings.GMS_BASE_URL}/generativelanguage.googleapis.com'
        f'/v1beta/models/{settings.GEMINI_MODEL}:generateContent'
    )
    body = {
        'systemInstruction': {'parts': [{'text': system}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_msg}]}],
        'generationConfig': {
            'responseMimeType': 'application/json',
            'responseSchema': _OUTPUT_SCHEMA,
            'temperature': 0.4,
        },
    }
    resp = httpx.post(
        url,
        params={'key': settings.GMS_KEY},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    data = json.loads(resp.json()['candidates'][0]['content']['parts'][0]['text'])
    bundles = _attach_bundles(data.get('bundles', []), limit)
    return {
        'summary': data.get('summary', ''),
        'bundles': bundles,
        'items': [it for b in bundles for it in b['items']],
        'source': 'ai',
    }


# ---------------------------------------------------------------------------
# 규칙 기반 폴백 (키 없음/오류 시) — 번들 형태로 반환
# ---------------------------------------------------------------------------
def _rule_recommend(corpus, signals, limit):
    """관심·인기·EBTI 보완 영역 가중 점수로 정렬 후 카테고리별 번들 구성."""
    weak_tags = []
    ebti = signals.get('ebti') or {}
    for b in (ebti.get('breakdown') or []):
        if not b.get('strong'):
            weak_tags += b.get('tags', [])

    scored = []
    for c in corpus:
        score = c['likes'] * 2 + c['views'] / 100
        for kw in weak_tags:
            if kw and (kw in c['title'] or kw in (c['summary'] or '')):
                score += 30
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [c for _, c in scored[:limit]]

    # 카테고리별로 묶어 번들 구성
    groups = {}
    for c in top:
        groups.setdefault(c['category'], []).append(c)

    bundle_specs = []
    for cat, cs in groups.items():
        if any(kw in c['title'] or kw in (c['summary'] or '')
               for c in cs for kw in weak_tags if kw):
            storyline = f'EBTI 진단에서 보완하면 좋을 영역과 맞닿은 {cat} 콘텐츠를 모았어요.'
        else:
            storyline = f'많은 회원이 좋아한 인기 {cat} 콘텐츠예요.'
        bundle_specs.append({
            'title': f'{cat} 묶음',
            'storyline': storyline,
            'content_ids': [c['id'] for c in cs[:4]],
        })

    bundles = _attach_bundles(bundle_specs[:4], limit)
    return {
        'summary': '관심사와 인기 주제를 바탕으로 골라봤어요.',
        'bundles': bundles,
        'items': [it for b in bundles for it in b['items']],
        'source': 'rule',
    }


# ---------------------------------------------------------------------------
# 공통: 번들의 content_id → 실제 Content 객체 매칭
# ---------------------------------------------------------------------------
def _attach_bundles(bundle_specs, limit):
    """번들 스펙의 content_id를 실제 Content 와 매칭. 중복 제거·상한 적용."""
    from .serializers import ContentSerializer

    all_ids = [cid for b in bundle_specs for cid in b.get('content_ids', [])]
    by_id = {c.id: c for c in Content.objects.filter(id__in=all_ids)}

    used = set()
    bundles = []
    total = 0
    for b in bundle_specs:
        items = []
        for cid in b.get('content_ids', []):
            if total >= limit:
                break
            c = by_id.get(cid)
            if c and cid not in used:
                used.add(cid)
                total += 1
                items.append({
                    'content': ContentSerializer(c).data,
                    'reason': b.get('storyline', ''),
                })
        if items:
            bundles.append({
                'title': b.get('title', ''),
                'storyline': b.get('storyline', ''),
                'items': items,
            })
    return bundles
