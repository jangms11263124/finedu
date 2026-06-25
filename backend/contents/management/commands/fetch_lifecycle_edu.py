"""
공공데이터포털 '재정경제부_생애주기별 경제교육 정보' API에서
청년기 데이터를 가져와 Data/lifecycle_edu_youth.xlsx 에 저장합니다.

사용법:
  python manage.py fetch_lifecycle_edu
  python manage.py fetch_lifecycle_edu --stage 청년기        # 기본값
  python manage.py fetch_lifecycle_edu --stage all           # 전체 생애주기
  python manage.py fetch_lifecycle_edu --out Data/my.xlsx    # 출력 경로 지정

API 엔드포인트 (odcloud 자동변환):
  GET https://api.odcloud.kr/api/15067603/v1/uddi:1ab22605-a95f-489e-ac64-deba104d4f14

서비스키 설정:
  .env 파일의 PUBLIC_DATA_API_KEY 에 data.go.kr 인증키를 입력하세요.
"""

import os
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

API_URL = (
    "https://api.odcloud.kr/api/15067603/v1"
    "/uddi:1ab22605-a95f-489e-ac64-deba104d4f14"
)

COLUMNS = ["생애주기", "기관명", "오프라인 교육", "온라인 교육", "링크주소"]


class Command(BaseCommand):
    help = "공공데이터포털에서 생애주기별 경제교육 정보를 가져옵니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--stage",
            default="청년기",
            help="필터링할 생애주기 (기본값: 청년기, 'all' 이면 전체)",
        )
        parser.add_argument(
            "--out",
            default="Data/lifecycle_edu_youth.xlsx",
            help="저장할 Excel 파일 경로 (기본값: Data/lifecycle_edu_youth.xlsx)",
        )

    def handle(self, *args, **options):
        service_key = os.environ.get("PUBLIC_DATA_API_KEY", "").strip()
        if not service_key:
            raise CommandError(
                "PUBLIC_DATA_API_KEY가 설정되지 않았습니다.\n"
                ".env 파일에 PUBLIC_DATA_API_KEY=<인증키> 를 추가하세요.\n"
                "인증키 발급: https://www.data.go.kr → 마이페이지 → 인증키 발급"
            )

        stage_filter = options["stage"]
        out_path = Path(settings.BASE_DIR) / options["out"]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        self.stdout.write("공공데이터 API 호출 중...")
        rows = self._fetch_all(service_key)
        self.stdout.write(f"  전체 {len(rows)}건 수신")

        if stage_filter != "all":
            rows = [r for r in rows if r.get("생애주기", "") == stage_filter]
            self.stdout.write(f"  '{stage_filter}' 필터 후 {len(rows)}건")

        if not rows:
            raise CommandError(f"'{stage_filter}' 데이터가 없습니다.")

        self._save_excel(rows, out_path)
        self.stdout.write(self.style.SUCCESS(f"저장 완료 → {out_path}"))

        # 결과 미리보기
        self.stdout.write("\n[미리보기]")
        for r in rows:
            self.stdout.write(
                f"  · {r.get('기관명','')}: {r.get('온라인 교육','')[:50]}"
            )

    def _fetch_all(self, service_key: str) -> list[dict]:
        """페이지네이션을 고려해 전체 데이터를 가져옵니다."""
        params = {
            "serviceKey": service_key,
            "page": 1,
            "perPage": 100,
            "returnType": "json",
        }
        try:
            resp = requests.get(API_URL, params=params, timeout=15)
        except requests.RequestException as e:
            raise CommandError(f"API 요청 실패: {e}")

        if resp.status_code != 200:
            raise CommandError(
                f"API 응답 오류 {resp.status_code}: {resp.text[:300]}"
            )

        try:
            payload = resp.json()
        except ValueError:
            raise CommandError(f"JSON 파싱 실패: {resp.text[:300]}")

        # odcloud 응답 구조: {"data": [...], "totalCount": N, ...}
        if "data" not in payload:
            raise CommandError(f"예상치 못한 응답 구조: {list(payload.keys())}")

        return payload["data"]

    def _save_excel(self, rows: list[dict], path: Path) -> None:
        try:
            import openpyxl
        except ImportError:
            raise CommandError("openpyxl이 필요합니다: pip install openpyxl")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "청년기 경제교육"

        # 헤더: API 컬럼 순서 유지
        actual_cols = list(rows[0].keys()) if rows else COLUMNS
        ws.append(actual_cols)

        for row in rows:
            ws.append([row.get(col, "") for col in actual_cols])

        # 열 너비 자동 조정
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=0)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)

        wb.save(path)
