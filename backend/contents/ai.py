"""AI 콘텐츠 추천 (2단계 RAG 파이프라인).

구성:
  [1단계 · Retrieval] Gemini 2.5 Flash가 전체 콘텐츠 목록과 사용자 관심사/프로필을
    비교하여 가장 연관성 높은 Top 10 콘텐츠를 선별하고 각각 한 줄 요약 생성.
    GMS 인증: ?key=$GMS_KEY

  [2단계 · Generation] GPT-4o가 Gemini가 고른 10개 콘텐츠와 사용자 상세
    프로필(수준·선호도·EBTI 등)을 조합하여 3~4개짜리 추천 번들 2개를 JSON으로 생성.
    GMS 인증: Authorization: Bearer $GMS_KEY

GMS_KEY 가 없거나 오류가 나면 규칙 기반 추천(번들 형태)으로 자동 대체한다.
"""
import json
import logging

from django.conf import settings
from django.db.models import Count

from .models import Content

logger = logging.getLogger(__name__)

CORPUS_SIZE = 60  # Gemini에 넘길 후보 상한 (비용 제어)

# 1단계: Gemini가 반환하는 Top 10 구조
_RETRIEVE_SCHEMA = {
    'type': 'object',
    'properties': {
        'top_contents': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'one_line': {'type': 'string'},
                },
                'required': ['id', 'one_line'],
            },
        },
    },
    'required': ['top_contents'],
}

# 2단계: GPT-4o가 반환하는 번들 구조 (strict mode → additionalProperties 필수)
_BUNDLE_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'summary': {'type': 'string'},
        'bundles': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
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
    """추천 후보 콘텐츠 코퍼스. 이미 좋아요한 콘텐츠는 제외."""
    qs = Content.objects.annotate(_likes=Count('likes'))
    if exclude_ids:
        qs = qs.exclude(id__in=exclude_ids)
    qs = qs.order_by('-views')[:CORPUS_SIZE]
    return [
        {
            'id': c.id,
            'title': c.title,
            'summary': c.summary,
            'body': (c.body or '')[:800],
            'category': c.get_category_display(),
            'views': c.views,
            'likes': c._likes,
        }
        for c in qs
    ]


def _attendance_streak(user):
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
        liked_qs = user.liked_contents.all()
        liked_ids = list(liked_qs.values_list('id', flat=True))
        liked_cats = list(liked_qs.values_list('category', flat=True))
        liked_titles = list(
            liked_qs.order_by('-id').values_list('title', flat=True)[:8]
        )

        community = list(user.posts.values_list('title', flat=True)[:6])
        community += list(
            user.content_comments.values_list('content__title', flat=True)[:5]
        )
        community += list(user.liked_posts.values_list('title', flat=True)[:5])
        community = list(dict.fromkeys(t for t in community if t))

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
        streak = _attendance_streak(user)

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
            candidates = _retrieve(corpus, signals)
            result = _generate(candidates, signals, limit)
            result['signals_meta'] = signals_meta
            return result
        except Exception as exc:
            logger.warning('AI 추천 실패, 규칙 기반으로 대체: %s', exc)

    result = _rule_recommend(corpus, signals, limit)
    result['signals_meta'] = signals_meta
    return result


# ---------------------------------------------------------------------------
# 1단계 · Retrieval (Gemini 2.5 Flash)
# ---------------------------------------------------------------------------
def _retrieve(corpus, signals):
    """Gemini 2.5 Flash로 콘텐츠-사용자 관심사 매칭 → Top 10 + 한 줄 요약."""
    import httpx

    gemini_model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')

    ebti = signals.get('ebti') or {}
    weak_areas = [b['name'] for b in (ebti.get('breakdown') or []) if not b.get('strong')]
    strong_areas = [b['name'] for b in (ebti.get('breakdown') or []) if b.get('strong')]

    signal_lines = []
    if signals.get('liked_categories'):
        signal_lines.append(
            f"관심 카테고리: {', '.join(set(str(c) for c in signals['liked_categories']))}"
        )
    if signals.get('liked_titles'):
        signal_lines.append(f"좋아요한 콘텐츠: {', '.join(signals['liked_titles'])}")
    if signals.get('community_posts'):
        signal_lines.append(
            f"커뮤니티 활동 주제: {', '.join(signals['community_posts'][:5])}"
        )
    if signals.get('quiz_weak'):
        signal_lines.append(f"최근 틀린 퀴즈: {' / '.join(signals['quiz_weak'][:3])}")
    if strong_areas:
        signal_lines.append(f"EBTI 강점 영역: {', '.join(strong_areas)}")
    if weak_areas:
        signal_lines.append(f"EBTI 보완 영역: {', '.join(weak_areas)}")
    if signals.get('trending_topics'):
        signal_lines.append(f"인기 주제: {', '.join(signals['trending_topics'])}")
    signal_summary = '\n'.join(signal_lines) if signal_lines else '(신규 사용자, 활동 기록 없음)'

    corpus_json = json.dumps(
        [
            {
                'id': c['id'],
                'title': c['title'],
                'summary': c['summary'],
                'category': c['category'],
                'body_excerpt': c.get('body', '')[:400],
            }
            for c in corpus
        ],
        ensure_ascii=False,
    )

    prompt = (
        '당신은 금융 교육 플랫폼의 콘텐츠 추천 AI입니다.\n\n'
        '## 사용자 관심사 / 프로필\n'
        f'{signal_summary}\n\n'
        '## 전체 콘텐츠 목록 (JSON)\n'
        f'{corpus_json}\n\n'
        '위 사용자 프로필을 분석하여, 콘텐츠 목록 안에서 이 사용자에게 가장 연관성 높은 '
        'Top 10 콘텐츠를 선별하고 각각 한국어로 한 줄 요약(one_line)을 작성해 주세요. '
        '반드시 콘텐츠 목록에 존재하는 id만 사용하세요.'
    )

    url = (
        f'{settings.GMS_BASE_URL}/generativelanguage.googleapis.com'
        f'/v1beta/models/{gemini_model}:generateContent'
    )
    body = {
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {
            'responseMimeType': 'application/json',
            'responseSchema': _RETRIEVE_SCHEMA,
            'temperature': 0.2,
        },
    }
    resp = httpx.post(
        url,
        params={'key': settings.GMS_KEY},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    raw = resp.json()['candidates'][0]['content']['parts'][0]['text']
    data = json.loads(raw)

    corpus_by_id = {c['id']: c for c in corpus}
    results = []
    for item in data.get('top_contents', []):
        c = corpus_by_id.get(item['id'])
        if c:
            results.append({**c, 'one_line': item.get('one_line', '')})
    return results[:10]


# ---------------------------------------------------------------------------
# 2단계 · Generation (GPT-4o Structured Outputs)
# ---------------------------------------------------------------------------
def _generate(candidates, signals, limit):
    """GPT-4o로 Top 10 콘텐츠 + 사용자 상세 프로필 → 추천 번들 2개 생성."""
    import httpx

    ebti = signals.get('ebti') or {}
    weak_areas = [b['name'] for b in (ebti.get('breakdown') or []) if not b.get('strong')]
    strong_areas = [b['name'] for b in (ebti.get('breakdown') or []) if b.get('strong')]
    streak = signals.get('streak') or 0

    profile_lines = []
    if strong_areas:
        profile_lines.append(f'EBTI 강점 영역: {", ".join(strong_areas)}')
    if weak_areas:
        profile_lines.append(f'EBTI 보완 영역(진단 결과): {", ".join(weak_areas)}')
    if signals.get('liked_titles'):
        titles = signals['liked_titles'][:5]
        quoted = ', '.join(f'"{t}"' for t in titles)
        profile_lines.append(f'좋아요한 콘텐츠 제목: {quoted}')
    elif signals.get('liked_categories'):
        cats = ', '.join(set(str(c) for c in signals['liked_categories']))
        profile_lines.append(f'선호 카테고리: {cats}')
    if signals.get('community_posts'):
        posts = signals['community_posts'][:4]
        quoted_posts = ', '.join(f'"{p}"' for p in posts)
        profile_lines.append(f'커뮤니티 활동 주제(글·댓글·좋아요): {quoted_posts}')
    if signals.get('quiz_weak'):
        quiz_str = ' / '.join(signals['quiz_weak'][:3])
        profile_lines.append(f'최근 틀린 퀴즈(반드시 summary/storyline에 언급): {quiz_str}')
    if streak:
        level_hint = '심화 콘텐츠 우선 추천' if streak >= 7 else '입문~중급 콘텐츠 우선 추천'
        profile_lines.append(f'연속 출석: {streak}일 → {level_hint}')
    profile_summary = '\n'.join(profile_lines) if profile_lines else '(신규 사용자 — 활동 데이터 없음)'

    candidates_json = json.dumps(
        [
            {
                'id': c['id'],
                'title': c['title'],
                'summary': c['summary'],
                'category': c['category'],
                'one_line': c.get('one_line', ''),
            }
            for c in candidates
        ],
        ensure_ascii=False,
    )

    system = (
        '당신은 금융 교육 플랫폼 im fine edu의 AI 큐레이터입니다.\n'
        'Gemini가 선별한 추천 후보 콘텐츠 10개와 사용자 상세 프로필을 바탕으로, '
        '최적의 학습 경험을 위한 추천 번들(Bundle) 정확히 2개를 만들어 주세요.\n\n'
        '=== 텍스트 작성 핵심 원칙 ===\n'
        'summary와 storyline은 반드시 사용자의 실제 활동 데이터를 구체적으로 언급해야 합니다.\n'
        '절대로 "관심사를 바탕으로", "취향에 맞게" 같은 막연한 표현만 쓰지 마세요.\n\n'
        '[summary 작성법] 2~3문장. 아래 데이터 중 실제로 존재하는 것만 골라 언급하세요.\n'
        '  • 좋아요한 콘텐츠 → 제목을 직접 인용: "\'ETF 투자 시작하기\' 같은 콘텐츠를 즐겨 보셨네요"\n'
        '  • 커뮤니티 글/댓글 → 주제 언급: "커뮤니티에 부동산 관련 글도 올리셨더라고요"\n'
        '  • 퀴즈 약점 → 구체적 언급: "최근 예금자보호 문제를 틀리셨는데"\n'
        '  • EBTI 보완 영역 → 진단 결과 언급: "EBTI 진단에서 소비 습관 영역이 보완 포인트로 나왔어요"\n'
        '  • 연속 출석 → 학습 의지 칭찬: "벌써 5일 연속 출석 중이시네요!"\n'
        '  데이터가 전혀 없으면(신규 사용자): "아직 활동 기록이 많지 않지만, 인기 콘텐츠 중심으로 골라봤어요!"\n\n'
        '[storyline 작성법] 각 번들마다 2~3문장. 이 번들이 해당 사용자에게 왜 맞는지 근거를 대세요.\n'
        '  • 퀴즈에서 틀린 개념과 연결되는 콘텐츠가 있으면: "퀴즈에서 헷갈리셨던 ○○ 개념을 여기서 확실히 잡을 수 있어요."\n'
        '  • 좋아요한 콘텐츠와 카테고리/주제가 이어지면: "\'○○\' 콘텐츠를 좋아하셨으니 이 번들도 잘 맞을 거예요."\n'
        '  • 커뮤니티 글 주제와 연결되면: "커뮤니티에서 관심 보이신 ○○ 주제를 더 깊이 다뤘어요."\n'
        '  • EBTI 보완 영역과 연결되면: "EBTI에서 보완이 필요하다고 나온 ○○ 영역 콘텐츠예요."\n\n'
        '=== 구성 규칙 ===\n'
        '- 번들마다 3~4개 콘텐츠를 묶어 하나의 학습 흐름을 구성하세요.\n'
        '- 두 번들에 같은 콘텐츠를 중복 사용하지 마세요.\n'
        '- content_ids는 제공된 후보 목록의 id만 사용하세요.\n'
        '- 연속 출석 7일 이상이면 심화 콘텐츠, 미만이면 입문 콘텐츠를 우선하세요.'
    )
    user_msg = (
        f'## 사용자 상세 프로필\n{profile_summary}\n\n'
        f'## Gemini 선별 Top 10 콘텐츠\n{candidates_json}\n\n'
        '위 프로필의 실제 데이터(좋아요한 콘텐츠 제목, 커뮤니티 주제, 퀴즈 약점, EBTI 결과 등)를 '
        'summary와 storyline에 구체적으로 녹여 주세요.'
    )

    url = f'{settings.GMS_BASE_URL}/api.openai.com/v1/chat/completions'
    body = {
        'model': 'gpt-4o',
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user_msg},
        ],
        'response_format': {
            'type': 'json_schema',
            'json_schema': {
                'name': 'recommendation',
                'schema': _BUNDLE_SCHEMA,
                'strict': True,
            },
        },
        'temperature': 0.4,
    }
    resp = httpx.post(
        url,
        headers={'Authorization': f'Bearer {settings.GMS_KEY}'},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    data = json.loads(resp.json()['choices'][0]['message']['content'])
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
    """관심·인기·EBTI 보완 영역 가중 점수로 정렬 후 카테고리별 번들 2개 구성."""
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

    groups = {}
    for c in top:
        groups.setdefault(c['category'], []).append(c)

    bundle_specs = []
    for cat, cs in groups.items():
        if any(
            kw in c['title'] or kw in (c['summary'] or '')
            for c in cs
            for kw in weak_tags
            if kw
        ):
            storyline = f'EBTI 진단에서 보완하면 좋을 영역과 맞닿은 {cat} 콘텐츠를 모았어요.'
        else:
            storyline = f'많은 회원이 좋아한 인기 {cat} 콘텐츠예요.'
        bundle_specs.append({
            'title': f'{cat} 묶음',
            'storyline': storyline,
            'content_ids': [c['id'] for c in cs[:4]],
        })

    bundles = _attach_bundles(bundle_specs[:2], limit)
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
