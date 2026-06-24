"""AI 콘텐츠 추천 (RAG).

RAG 구성:
  - 검색(Retrieve): 콘텐츠 DB에서 후보 코퍼스를 만든다.
  - 보강(Augment): 사용자 신호(EBTI 결과·관심 카테고리·커뮤니티 글·지역)와
    최근 인기 주제를 프롬프트에 함께 넣는다.
  - 생성(Generate): Claude가 후보 중 맞춤 콘텐츠를 골라 추천 이유를 생성한다.

ANTHROPIC_API_KEY 가 없으면 규칙 기반 추천으로 자동 대체한다.
"""
import json

from django.conf import settings
from django.db.models import Count

from .models import Content

MODEL = 'claude-opus-4-8'

# 구조화 출력 스키마 (content_id + 추천 이유 목록)
_OUTPUT_SCHEMA = {
    'type': 'object',
    'properties': {
        'summary': {'type': 'string'},
        'recommendations': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'content_id': {'type': 'integer'},
                    'reason': {'type': 'string'},
                },
                'required': ['content_id', 'reason'],
                'additionalProperties': False,
            },
        },
    },
    'required': ['summary', 'recommendations'],
    'additionalProperties': False,
}


def _corpus():
    """추천 후보 콘텐츠 코퍼스 (검색 단계)."""
    qs = Content.objects.annotate(_likes=Count('likes')).order_by('-views')[:50]
    return [
        {
            'id': c.id,
            'title': c.title,
            'summary': c.summary,
            'category': c.get_category_display(),
            'views': c.views,
            'likes': c._likes,
        }
        for c in qs
    ]


def _user_signals(user, ebti, region):
    """사용자 맞춤 신호 (보강 단계)."""
    liked = list(
        user.liked_contents.values_list('category', flat=True)
    ) if user and user.is_authenticated else []
    posts = list(
        user.posts.values_list('title', flat=True)[:10]
    ) if user and user.is_authenticated else []

    # 최근 인기 경제 주제 (조회·좋아요 상위 카테고리)
    top = (
        Content.objects.values('category')
        .annotate(v=Count('id'))
        .order_by('-v')[:3]
    )
    return {
        'ebti': ebti or None,
        'region': region or (getattr(user, 'region', '') if user else ''),
        'liked_categories': liked,
        'community_posts': posts,
        'trending_topics': [t['category'] for t in top],
    }


def recommend(user, ebti=None, region='', limit=6):
    """추천 결과 dict 반환: {summary, items:[{content, reason}], source}."""
    corpus = _corpus()
    signals = _user_signals(user, ebti, region)

    if settings.ANTHROPIC_API_KEY:
        try:
            return _ai_recommend(corpus, signals, limit)
        except Exception as exc:  # API 오류 시 규칙 기반으로 대체
            print('AI 추천 실패, 규칙 기반으로 대체:', exc)

    return _rule_recommend(corpus, signals, limit)


def _ai_recommend(corpus, signals, limit):
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    system = (
        '당신은 금융 교육 플랫폼 finedu의 콘텐츠 추천 AI입니다. '
        '주어진 콘텐츠 목록(corpus) 중에서만 사용자에게 가장 잘 맞는 콘텐츠를 골라 '
        '추천 이유를 한국어로 친근하게 작성하세요. corpus에 없는 콘텐츠는 추천하지 마세요.'
    )
    user_msg = (
        f'## 사용자 신호\n{json.dumps(signals, ensure_ascii=False)}\n\n'
        f'## 콘텐츠 목록(corpus)\n{json.dumps(corpus, ensure_ascii=False)}\n\n'
        f'위 사용자에게 맞는 콘텐츠를 corpus의 content_id 기준으로 {limit}개 골라주세요. '
        'EBTI 결과의 보완 영역, 관심 카테고리, 커뮤니티 글 주제, 최근 인기 주제, 지역을 '
        '종합적으로 반영하고, 각 추천마다 한두 문장의 개인화된 이유를 써주세요. '
        'summary에는 전체 추천 방향을 한 문장으로 요약하세요.'
    )

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{'role': 'user', 'content': user_msg}],
        output_config={
            'format': {'type': 'json_schema', 'schema': _OUTPUT_SCHEMA},
            'effort': 'low',
        },
    )
    text = next(b.text for b in resp.content if b.type == 'text')
    data = json.loads(text)
    items = _attach_contents(data['recommendations'], limit)
    return {'summary': data.get('summary', ''), 'items': items, 'source': 'ai'}


def _rule_recommend(corpus, signals, limit):
    """규칙 기반 추천 (키 없음/오류 시). 관심·인기·EBTI 보완 영역 가중."""
    liked = set(signals['liked_categories'])
    trending = set(signals['trending_topics'])

    # EBTI 보완 영역 태그 → 키워드
    weak_tags = []
    ebti = signals.get('ebti') or {}
    for b in (ebti.get('breakdown') or []):
        if not b.get('strong'):
            weak_tags += b.get('tags', [])

    scored = []
    for c in corpus:
        score = c['likes'] * 2 + c['views'] / 100
        # 카테고리 코드 매핑이 어려우니 표시명 기준 가중은 생략하고 인기·키워드 위주
        for kw in weak_tags:
            if kw and (kw in c['title'] or kw in c['summary']):
                score += 30
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)

    recs = []
    for _, c in scored[:limit]:
        reason = '많은 회원이 좋아한 인기 콘텐츠예요.'
        if any(kw in c['title'] or kw in c['summary'] for kw in weak_tags if kw):
            reason = 'EBTI 진단에서 보완하면 좋을 영역과 맞닿아 있어 추천해요.'
        elif c['category'] in {signals['region']}:
            reason = '관심 지역과 관련된 콘텐츠예요.'
        recs.append({'content_id': c['id'], 'reason': reason})

    items = _attach_contents(recs, limit)
    summary = '관심사와 인기 주제를 바탕으로 골라봤어요.'
    return {'summary': summary, 'items': items, 'source': 'rule'}


def _attach_contents(recs, limit):
    """추천 결과의 content_id를 실제 Content 객체와 매칭."""
    from .serializers import ContentSerializer

    ids = [r['content_id'] for r in recs][:limit]
    by_id = {c.id: c for c in Content.objects.filter(id__in=ids)}
    items = []
    for r in recs:
        c = by_id.get(r['content_id'])
        if c:
            items.append({
                'content': ContentSerializer(c).data,
                'reason': r['reason'],
            })
    return items
