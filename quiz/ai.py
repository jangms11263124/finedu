"""오늘의 퀴즈 AI 생성 — SSAFY GMS 게이트웨이 경유 Gemini.

매일 다른 경제·금융 상식 퀴즈를 생성한다. glossary 용어 일부를 영감으로
프롬프트에 넣어 다양하고 주제에 맞는 문제가 나오게 한다.
GMS_KEY 가 없거나 오류가 나면 정적 폴백 퀴즈로 자동 대체한다.
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# Gemini structured output 스키마 (responseSchema)
_SCHEMA = {
    'type': 'object',
    'properties': {
        'question': {'type': 'string'},
        'options': {'type': 'array', 'items': {'type': 'string'}},
        'answer_index': {'type': 'integer'},
        'explanation': {'type': 'string'},
    },
    'required': ['question', 'options', 'answer_index', 'explanation'],
}

# AI 실패 시 사용할 정적 퀴즈 풀 (날짜로 회전)
_FALLBACK = [
    {
        'question': '금리가 오르면 일반적으로 채권 가격은?',
        'options': ['올라간다', '내려간다'],
        'answer_index': 1,
        'explanation': '금리와 채권 가격은 반대로 움직여요. 금리가 오르면 기존 채권의 '
                       '매력이 떨어져 가격이 내려갑니다.',
    },
    {
        'question': '분산 투자의 가장 큰 목적은?',
        'options': ['수익 극대화', '위험 분산'],
        'answer_index': 1,
        'explanation': '여러 자산에 나눠 담으면 한쪽이 손실이어도 충격을 줄일 수 있어요.',
    },
    {
        'question': '인플레이션이 심할 때 현금의 실질 가치는?',
        'options': ['올라간다', '내려간다'],
        'answer_index': 1,
        'explanation': '물가가 오르면 같은 돈으로 살 수 있는 양이 줄어 현금 가치가 떨어져요.',
    },
    {
        'question': '예금자보호법상 1인당 보호 한도는 보통 얼마까지일까요?',
        'options': ['1천만 원', '5천만 원', '1억 원'],
        'answer_index': 1,
        'explanation': '한 금융회사당 원금과 이자를 합쳐 5천만 원까지 보호돼요.',
    },
    {
        'question': '주식에서 "분산투자"와 거리가 먼 것은?',
        'options': ['여러 종목에 나눠 투자', '한 종목에 몰아 투자'],
        'answer_index': 1,
        'explanation': '한 종목에 몰아넣는 건 위험을 키우는 집중투자예요.',
    },
    {
        'question': '복리 효과를 가장 잘 설명한 것은?',
        'options': ['원금에만 이자가 붙는다', '이자에 다시 이자가 붙는다'],
        'answer_index': 1,
        'explanation': '복리는 이자가 원금에 더해져 그 합계에 또 이자가 붙는 구조예요.',
    },
    {
        'question': 'ETF에 대한 설명으로 옳은 것은?',
        'options': ['거래소에 상장돼 주식처럼 사고팔 수 있다', '만기까지 팔 수 없다'],
        'answer_index': 0,
        'explanation': 'ETF는 상장지수펀드로, 주식처럼 실시간 매매할 수 있어요.',
    },
]


def generate_quiz(seed_date):
    """오늘의 퀴즈 dict 반환: {question, options, answer_index, explanation, source}."""
    if settings.GMS_KEY:
        try:
            return _ai_quiz(seed_date)
        except Exception as exc:  # API 오류 시 폴백
            logger.warning('퀴즈 AI 생성 실패, 폴백 사용: %s', exc)
    return _fallback_quiz(seed_date)


def _terms_hint(n=6):
    """glossary 용어 일부를 영감용 힌트로 추출."""
    try:
        from glossary.models import Term
        qs = list(Term.objects.order_by('?')[:n])
        return [f'{t.term}: {t.description[:60]}' for t in qs]
    except Exception:
        return []


def _ai_quiz(seed_date):
    import httpx

    hints = _terms_hint()
    system = (
        '당신은 금융 교육 플랫폼 im fine edu의 퀴즈 출제자입니다. '
        '경제·금융·투자 상식에 관한 객관식 퀴즈를 정확히 하나 만드세요. '
        '보기(options)는 2~4개, 정답은 정확히 1개이며, answer_index는 0부터 시작하는 '
        '정답 보기의 인덱스입니다. 문제(question)는 한국어로 간결하게, '
        'explanation(해설)은 1~2문장으로 친근하게 작성하세요. '
        '너무 어렵거나 지엽적이지 않은, 초보자도 흥미로워할 문제가 좋아요.'
    )
    hint_block = ('\n- ' + '\n- '.join(hints)) if hints else ' (없음)'
    user_msg = (
        f'오늘 날짜: {seed_date.isoformat()} — 날짜마다 매번 다른 주제·문제를 내세요.\n'
        f'참고 용어(영감용, 반드시 사용할 필요는 없음):{hint_block}'
    )

    url = (
        f'{settings.GMS_BASE_URL}/generativelanguage.googleapis.com'
        f'/v1beta/models/{settings.GEMINI_MODEL}:generateContent'
    )
    body = {
        'systemInstruction': {'parts': [{'text': system}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_msg}]}],
        'generationConfig': {
            'responseMimeType': 'application/json',
            'responseSchema': _SCHEMA,
            'temperature': 1.1,  # 다양성 ↑
        },
    }
    resp = httpx.post(
        url, params={'key': settings.GMS_KEY}, json=body, timeout=60
    )
    resp.raise_for_status()
    data = json.loads(resp.json()['candidates'][0]['content']['parts'][0]['text'])
    return _validated(data, 'ai')


def _validated(data, source):
    """AI 응답 형식 검증·정규화. 어긋나면 예외 → 폴백 유도."""
    options = [str(o) for o in (data.get('options') or [])][:4]
    try:
        idx = int(data.get('answer_index', 0))
    except (TypeError, ValueError):
        idx = -1
    if len(options) < 2 or not (0 <= idx < len(options)):
        raise ValueError('퀴즈 형식 오류')
    return {
        'question': str(data.get('question', ''))[:300],
        'options': options,
        'answer_index': idx,
        'explanation': str(data.get('explanation', ''))[:500],
        'source': source,
    }


def _fallback_quiz(seed_date):
    q = _FALLBACK[seed_date.toordinal() % len(_FALLBACK)]
    return {**q, 'source': 'fallback'}
