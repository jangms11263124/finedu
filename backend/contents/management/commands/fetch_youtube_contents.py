"""
YouTube Data API v3 로 사회초년생 금융·경제 교육 영상을 수집해
Content 모델에 임포트합니다. 각 영상의 설명은 Gemini Flash(GMS 경유)로 AI 요약합니다.

사용법:
  python manage.py fetch_youtube_contents
  python manage.py fetch_youtube_contents --count 150       # 기본값
  python manage.py fetch_youtube_contents --clear           # 기존 YouTube 임포트 삭제 후 재수집
  python manage.py fetch_youtube_contents --no-summarize    # AI 요약 없이 원문 저장

API 키 설정:
  .env 의 YOUTUBE_API_KEY  — YouTube Data API v3 키
  .env 의 GMS_KEY          — SSAFY GMS 게이트웨이 키 (Gemini Flash 요약용)
"""

import os
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from contents.models import Content

SOURCE_TAG = "[YouTube]"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
GEMINI_MODEL = "gemini-2.5-flash-lite"

# ── 검색 쿼리 (기본 사회초년생 금융 + EBTI 5개 주제 별 특화 쿼리) ──────────────
QUERIES = [
    # ── 기본 사회초년생 금융 ──────────────────────────────────────────────────
    "사회초년생 금융 교육",
    "사회초년생 재테크 기초",
    "경제 기초 강의 입문",
    "경제 용어 기초 설명",
    "물가 금리 환율 쉬운 설명",
    "직장인 세금 환급 방법",
    "사회초년생 연말정산 방법",
    "청년 청약 주택 저축",

    # ── EBTI 1 : 소비(지출) 관리 ─────────────────────────────────────────────
    # tags: 소비지출관리, 소비지출, 소비, 지출, 합리적소비, 신용관리, 신용카드, 체크카드
    "합리적 소비 지출 관리 방법",
    "사회초년생 통장 쪼개기",
    "월급 관리 저축 방법",
    "가계부 지출 줄이기 절약",
    "소비 습관 개선 방법 절약",
    "신용카드 체크카드 사용법 비교",
    "신용점수 관리 방법 신용등급",
    "과소비 방지 소비 계획 세우기",
    "지출 줄이기 고정비 변동비 관리",

    # ── EBTI 2 : 자산 관리 ───────────────────────────────────────────────────
    # tags: 자산관리, 자산, 저축, 투자, 포트폴리오, 예금적금, 부채관리, 금융상품
    "포트폴리오 분산투자 방법 초보",
    "예금 적금 차이 비교",
    "주식 투자 기초 교육",
    "금융상품 종류 비교 설명",
    "ISA 연금저축 ETF 초보",
    "부채 대출 관리 방법",
    "목돈 마련 방법 사회초년생",
    "자산 배분 투자 전략 초보",
    "채권 ETF 펀드 차이 설명",
    "월급 저축 투자 비율 방법",
    "재테크 순서 사회초년생",

    # ── EBTI 3 : 변화 대응 ───────────────────────────────────────────────────
    # tags: 경제이슈, 기준금리, 물가, 환율, 정부정책, 경제전망, 팩트체크
    "기준금리 변화 재테크 영향",
    "환율 달러 경제 영향 설명",
    "인플레이션 물가 상승 대처법",
    "청년 금융 지원 정책 혜택",
    "경제 뉴스 이해하는 방법",
    "정부 청년 지원 제도 총정리",
    "금리 인상 하락 재테크 전략",
    "경제 지표 보는 방법 GDP 물가",
    "환율 상승 하락 나에게 미치는 영향",

    # ── EBTI 4 : 위기 관리 ───────────────────────────────────────────────────
    # tags: 위기관리, 신용위험관리, 보이스피싱, 소비자보호, 소비자권리, 금융사기예방
    "보이스피싱 금융사기 예방 방법",
    "소비자 권리 환불 피해구제",
    "비상금 위기 대비 재테크",
    "금융 사기 유형 피해 사례",
    "신용 위기 대처 방법 연체",
    "소비자 피해 대처법 신고 방법",
    "불법 스팸 스미싱 보이스피싱 예방",
    "긴급 자금 마련 비상금 통장",

    # ── EBTI 5 : 노후 대비 ───────────────────────────────────────────────────
    # tags: 노후대비, 노후설계, 연금, 보험, 은퇴자산, 생애주기
    "노후 연금 은퇴 준비 방법",
    "IRP 퇴직연금 연금저축 비교",
    "생애주기 재무설계 방법",
    "실손보험 생명보험 가입 방법",
    "국민연금 이해 수령 방법",
    "노후 준비 20대 30대 지금 시작",
    "퇴직금 IRP 운용 방법",
    "보험 종류 선택 방법 초보",
    "은퇴 후 자산 관리 생활비",
]

# ── 카테고리 매핑 (EBTI 태그 포함) ──────────────────────────────────────────
CATEGORY_MAP = {
    # 투자 계열
    "재테크": "invest",
    "주식": "invest",
    "투자": "invest",
    "포트폴리오": "invest",
    "ETF": "invest",
    "채권": "invest",
    "펀드": "invest",
    "분산": "invest",
    "자산배분": "invest",
    # 저축 계열
    "저축": "saving",
    "적금": "saving",
    "예금": "saving",
    "절약": "saving",
    "가계부": "saving",
    "통장": "saving",
    "목돈": "saving",
    "비상금": "saving",
    "월급": "saving",
    # 금융상품·신용 계열
    "금융상품": "finance",
    "금융 상품": "finance",
    "보험": "finance",
    "대출": "finance",
    "연금": "finance",
    "IRP": "finance",
    "ISA": "finance",
    "신용": "finance",
    "부채": "finance",
    "퇴직": "finance",
    "국민연금": "finance",
    "실손": "finance",
    "생명보험": "finance",
    # 경제·변화 대응 계열
    "경제": "economy",
    "기초": "economy",
    "금리": "economy",
    "물가": "economy",
    "환율": "economy",
    "인플레이션": "economy",
    "경제지표": "economy",
    "경제전망": "economy",
    "정부정책": "economy",
    "팩트체크": "economy",
    "GDP": "economy",
    # 사회·위기 관리 계열
    "사회": "society",
    "소비자": "society",
    "사기": "society",
    "보이스피싱": "society",
    "스미싱": "society",
    "피해구제": "society",
    "노후": "society",
    "은퇴": "society",
    "생애주기": "society",
    "위기": "society",
    "연체": "society",
}


def guess_category(title: str, description: str) -> str:
    text = title + " " + description
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in text:
            return cat
    return "economy"


class Command(BaseCommand):
    help = "YouTube Data API로 사회초년생 금융·경제 + EBTI 5개 주제 교육 영상을 수집합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=150,
            help="수집할 영상 수 (기본값: 150)",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="summary에 [YouTube] 태그가 있는 기존 레코드를 삭제한 뒤 재수집",
        )
        parser.add_argument(
            "--no-summarize", action="store_true",
            help="Gemini AI 요약을 건너뛰고 원본 설명 저장",
        )

    def handle(self, *args, **options):
        api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
        if not api_key:
            raise CommandError(
                "YOUTUBE_API_KEY가 설정되지 않았습니다.\n"
                ".env 파일에 YOUTUBE_API_KEY=<키> 를 추가하세요."
            )

        use_ai = not options["no_summarize"]
        gms_key = settings.GMS_KEY
        if use_ai and not gms_key:
            self.stderr.write("GMS_KEY가 없어 AI 요약을 건너뜁니다.")
            use_ai = False

        if options["clear"]:
            deleted, _ = Content.objects.filter(summary__contains=SOURCE_TAG).delete()
            self.stdout.write(f"기존 {deleted}건 삭제 완료")

        target = options["count"]
        self.stdout.write(
            f"수집 목표: {target}개 | 쿼리 수: {len(QUERIES)}개 | AI 요약: {'ON' if use_ai else 'OFF'}\n"
        )

        video_ids = self._search_videos(api_key, target)
        self.stdout.write(f"검색된 영상 ID {len(video_ids)}개 → 상세 정보 수집 중...")

        details = self._fetch_video_details(api_key, video_ids)
        self.stdout.write(f"상세 정보 {len(details)}건 수집 완료\n")

        if use_ai:
            self.stdout.write(f"Gemini({GEMINI_MODEL}) AI 요약 시작...")

        created = 0
        for i, v in enumerate(details, 1):
            snippet = v.get("snippet", {})
            stats = v.get("statistics", {})
            youtube_id = v["id"]

            title = snippet.get("title", "")[:200]
            description = snippet.get("description", "")
            channel = snippet.get("channelTitle", "")
            views = int(stats.get("viewCount", 0))
            category = guess_category(title, description)

            if use_ai and description:
                body = self._summarize(title, description, gms_key)
                label = "AI요약"
            else:
                body = description[:1000]
                label = "원문"

            summary = f"{SOURCE_TAG} {channel}"
            Content.objects.create(
                title=title,
                summary=summary[:300],
                body=body,
                category=category,
                youtube_id=youtube_id,
                views=views,
                is_recommended=True,
            )
            safe = title[:45].encode('cp949', errors='replace').decode('cp949')
            self.stdout.write(f"  [{i:03d}/{len(details)}] ({label}/{category}) {safe}")
            created += 1

        self.stdout.write(self.style.SUCCESS(f"\n수집 완료: {created}건 저장됨"))

    # ── YouTube API ──────────────────────────────────────────────────────────

    def _search_videos(self, api_key: str, target: int) -> list[str]:
        # 쿼리당 최소 3개, 최대 50개 요청해 고르게 분배
        per_query = max(target // len(QUERIES) + 1, 3)
        seen: set[str] = set()
        ids: list[str] = []

        for query in QUERIES:
            if len(ids) >= target:
                break
            params = {
                "key": api_key,
                "part": "id",
                "q": query,
                "type": "video",
                "videoCategoryId": "27",   # Education
                "relevanceLanguage": "ko",
                "regionCode": "KR",
                "maxResults": min(per_query, 50),
                "safeSearch": "moderate",
            }
            try:
                resp = requests.get(SEARCH_URL, params=params, timeout=15)
                resp.raise_for_status()
            except requests.RequestException as e:
                self.stderr.write(f"검색 오류 ({query}): {e}")
                continue

            for item in resp.json().get("items", []):
                vid = item.get("id", {}).get("videoId")
                if vid and vid not in seen:
                    seen.add(vid)
                    ids.append(vid)
                    if len(ids) >= target:
                        break

            self.stdout.write(f"  '{query[:30]}' → 누적 {len(ids)}건")
            time.sleep(0.3)

        # Education 카테고리 필터 없이 보충
        if len(ids) < target:
            self.stdout.write("Education 필터 없이 보충 수집 중...")
            for query in QUERIES:
                if len(ids) >= target:
                    break
                params = {
                    "key": api_key, "part": "id", "q": query,
                    "type": "video", "relevanceLanguage": "ko",
                    "regionCode": "KR", "maxResults": 10,
                }
                try:
                    resp = requests.get(SEARCH_URL, params=params, timeout=15)
                    resp.raise_for_status()
                except requests.RequestException:
                    continue
                for item in resp.json().get("items", []):
                    vid = item.get("id", {}).get("videoId")
                    if vid and vid not in seen:
                        seen.add(vid)
                        ids.append(vid)
                        if len(ids) >= target:
                            break
                time.sleep(0.3)

        return ids[:target]

    def _fetch_video_details(self, api_key: str, video_ids: list[str]) -> list[dict]:
        results = []
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            params = {"key": api_key, "part": "snippet,statistics", "id": ",".join(chunk)}
            try:
                resp = requests.get(VIDEOS_URL, params=params, timeout=15)
                resp.raise_for_status()
                results.extend(resp.json().get("items", []))
            except requests.RequestException as e:
                self.stderr.write(f"상세 조회 오류: {e}")
            time.sleep(0.3)
        return results

    # ── Gemini AI 요약 (GMS 경유) ────────────────────────────────────────────

    def _summarize(self, title: str, description: str, gms_key: str) -> str:
        """YouTube 영상 제목+설명 → Gemini Flash로 한국어 요약."""
        prompt = (
            f"다음은 YouTube 영상의 제목과 설명입니다.\n"
            f"사회초년생을 위한 금융·경제 관점에서 이 영상의 핵심 내용을 "
            f"한국어로 3~4문장으로 요약해주세요. "
            f"어떤 내용을 배울 수 있는지 구체적으로 써주세요.\n\n"
            f"제목: {title}\n"
            f"설명:\n{description[:2000]}"
        )
        url = (
            f"{settings.GMS_BASE_URL}"
            f"/generativelanguage.googleapis.com"
            f"/v1beta/models/{GEMINI_MODEL}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
            },
        }
        try:
            resp = requests.post(url, params={"key": gms_key}, json=payload, timeout=30)
            resp.raise_for_status()
            parts = resp.json()["candidates"][0]["content"]["parts"]
            text = "".join(
                p["text"] for p in parts if not p.get("thought", False)
            ).strip()
            time.sleep(0.5)
            return text
        except Exception as e:
            self.stderr.write(f"AI 요약 실패 ({title[:30]}): {e}")
            return description[:1000]
