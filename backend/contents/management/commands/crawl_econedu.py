"""
경제배움e+ (econedu.go.kr) 온라인 교육과정 크롤러

사용법:
  python manage.py crawl_econedu
  python manage.py crawl_econedu --count 200        # 최대 수집 건수 (기본: 150)
  python manage.py crawl_econedu --types ALL ON MX  # 크롤할 카테고리 선택
  python manage.py crawl_econedu --no-detail        # 상세 설명 없이 기본 정보만 저장
  python manage.py crawl_econedu --clear            # 기존 econedu 데이터 삭제 후 재수집

카테고리:
  ALL = 기본 교육과정 (약 8건)
  ON  = 이슈별 교육과정 (약 46건)
  MX  = 협력사 제공 교육과정 (약 280건)
"""

import re
import time

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from contents.models import Content

BASE_URL = "https://www.econedu.go.kr"
PAGE_SIZE = 36
SOURCE_TAG = "[econedu]"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

# econedu 카테고리 텍스트 → 내부 카테고리
CATEGORY_MAP = {
    "자산관리": "invest",
    "투자": "invest",
    "소비": "saving",
    "합리적 소비": "saving",
    "저축": "saving",
    "가계": "finance",
    "신용": "finance",
    "세금": "finance",
    "보험": "finance",
    "금융": "finance",
    "소비자보호": "society",
    "소비자권리": "society",
    "사기": "society",
    "위험": "society",
    "노후": "society",
    "은퇴": "society",
    "생애주기": "society",
}


def guess_category(cate_text: str) -> str:
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in cate_text:
            return cat
    return "economy"


class Command(BaseCommand):
    help = "경제배움e+ 온라인 교육과정을 크롤링해 Content 모델에 저장합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=150,
            help="최대 수집 건수 (기본: 150)",
        )
        parser.add_argument(
            "--types", nargs="+", default=["ALL", "ON", "MX"],
            help="크롤할 교육과정 분류: ALL ON MX (기본: 모두)",
        )
        parser.add_argument(
            "--no-detail", action="store_true",
            help="상세 설명(과정소개) 크롤링 건너뜀 — 속도 빠름",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="summary에 [econedu] 태그가 있는 기존 레코드를 삭제한 뒤 재수집",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = Content.objects.filter(summary__contains=SOURCE_TAG).delete()
            self.stdout.write(f"기존 {deleted}건 삭제 완료")

        target = options["count"]
        types = [t.upper() for t in options["types"]]
        fetch_detail = not options["no_detail"]

        self.stdout.write(
            f"수집 시작 | 분류: {', '.join(types)} | 목표: {target}건 | "
            f"상세 설명: {'ON' if fetch_detail else 'OFF'}\n"
        )

        session = requests.Session()
        session.headers.update(HEADERS)
        # 세션 쿠키 획득
        session.get(BASE_URL + "/user/learnEcon/ALL/menu/list", timeout=15)

        # 모든 카테고리에서 코스 수집 (앞 카테고리가 부족하면 뒤에서 채움)
        all_courses: list[dict] = []

        for cat in types:
            remaining = target - len(all_courses)
            if remaining <= 0:
                break
            self.stdout.write(f"\n[{cat}] 목록 수집 중... (남은 목표: {remaining}건)")
            courses = self._collect_list(session, cat, remaining)
            self.stdout.write(f"[{cat}] {len(courses)}건 수집됨")
            all_courses.extend(courses)
        self.stdout.write(f"\n전체 수집: {len(all_courses)}건 → 저장 시작\n")

        created = 0
        skipped = 0
        for i, course in enumerate(all_courses, 1):
            title = course["title"]

            # 중복 체크
            if Content.objects.filter(title=title, summary__contains=SOURCE_TAG).exists():
                safe = title[:40].encode("cp949", errors="replace").decode("cp949")
                self.stdout.write(f"  [{i:03d}] SKIP {safe}")
                skipped += 1
                continue

            body = ""
            if fetch_detail and course.get("course_id"):
                body = self._fetch_detail(session, course["course_id"], course.get("course_type", "ALL"))

            if not body:
                body = course.get("description", "")

            cate_text = course.get("cate", "")
            category = guess_category(cate_text)
            summary = f"{SOURCE_TAG} {course.get('org', '재정경제부')} | {cate_text}"

            content_obj = Content(
                title=title[:200],
                summary=summary[:300],
                body=body,
                category=category,
                external_url=course.get("detail_url", ""),
                views=course.get("views", 0),
                is_recommended=True,
            )

            # 썸네일 다운로드
            thumb_url = course.get("thumbnail_url", "")
            if thumb_url:
                try:
                    resp = session.get(thumb_url, timeout=15)
                    resp.raise_for_status()
                    fname = f"econedu_{course.get('course_id', i)}.png"
                    content_obj.thumbnail.save(
                        fname, ContentFile(resp.content), save=False
                    )
                except Exception as e:
                    self.stderr.write(f"  썸네일 실패: {str(e)[:60]}")

            content_obj.save()
            created += 1

            safe = title[:40].encode("cp949", errors="replace").decode("cp949")
            self.stdout.write(
                f"  [{i:03d}/{len(all_courses)}] ({category}/{course.get('course_type', '?')}) {safe}"
            )
            time.sleep(0.3)

        self.stdout.write(
            self.style.SUCCESS(f"\n완료: {created}건 저장 | {skipped}건 중복 스킵")
        )

    def _collect_list(self, session: requests.Session, cat: str, target: int) -> list[dict]:
        courses: list[dict] = []
        startno = 0
        page = 1
        url = f"{BASE_URL}/user/learnEcon/{cat}/selectData"
        referer = f"{BASE_URL}/user/learnEcon/{cat}/menu/list"

        while len(courses) < target:
            params = {
                "p_curculm_cat": cat,
                "s_curculm_main_cat": "",
                "s_curculm_midl_cat": "",
                "s_trgt_curculm_cat": "",
                "s_status": "",
                "p_pageno": str(page),
                "s_co_sprvsn_id": "",
                "s_searchSel": "",
                "s_search_input": "",
                "s_order": "",
                "startno": str(startno),
                "selectCnt": str(PAGE_SIZE),
            }
            try:
                resp = session.post(
                    url, data=params,
                    headers={"Referer": referer},
                    timeout=20,
                )
                resp.raise_for_status()
            except requests.RequestException as e:
                self.stderr.write(f"  목록 요청 오류 (page {page}): {e}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            found = self._parse_list_page(soup, cat)

            if not found:
                break  # 더 이상 데이터 없음

            courses.extend(found)
            self.stdout.write(f"  page {page}: {len(found)}건 (누적 {len(courses)}건)")

            if len(found) < PAGE_SIZE:
                break  # 마지막 페이지

            startno += PAGE_SIZE
            page += 1
            time.sleep(0.5)

        return courses[:target]

    def _parse_list_page(self, soup: BeautifulSoup, cat: str) -> list[dict]:
        courses = []
        # selectData는 <li> 태그를 직접 반환함
        items = soup.find_all("li", recursive=False)
        if not items:
            items = soup.select("li")

        for li in items:
            # 과정 제목
            tit_el = li.select_one("a.con-tit") or li.select_one(".con-tit")
            if not tit_el:
                continue
            title = tit_el.get_text(strip=True)
            if not title:
                continue

            # 과정 ID & 타입 (onclick에서 추출)
            course_id = ""
            course_type = cat
            for a in li.find_all("a", onclick=True):
                m = re.search(
                    r"fnCurculmDtl\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]",
                    a.get("onclick", ""),
                )
                if m:
                    course_id = m.group(1)
                    course_type = m.group(2)
                    break

            # 파트너 교육과정용 별도 처리
            if not course_id:
                for a in li.find_all("a", onclick=True):
                    m2 = re.search(r"fnDtlView\(['\"]([^'\"]+)['\"]", a.get("onclick", ""))
                    if m2:
                        course_id = m2.group(1)
                        break

            # 썸네일
            img = li.select_one(".con-img img")
            thumbnail_url = ""
            if img:
                src = img.get("src", "")
                thumbnail_url = BASE_URL + src if src.startswith("/") else src

            # 카테고리 텍스트
            cate_el = li.select_one(".con-cate")
            cate = cate_el.get_text(strip=True) if cate_el else ""

            # 기관명
            org_el = li.select_one(".organizer1")
            org = org_el.get_text(strip=True) if org_el else "재정경제부"

            # 조회수
            view_el = li.select_one(".icon-view")
            views = 0
            if view_el:
                nums = re.findall(r"\d+", view_el.get_text())
                views = int(nums[-1]) if nums else 0

            detail_url = (
                f"{BASE_URL}/user/learnEcon/{course_type}/learnEconDtl"
                f"?p_curculm_sn={course_id}&p_curculm_cat={course_type}"
                if course_id else ""
            )

            courses.append({
                "title": title,
                "course_id": course_id,
                "course_type": course_type,
                "thumbnail_url": thumbnail_url,
                "cate": cate,
                "org": org,
                "views": views,
                "detail_url": detail_url,
            })

        return courses

    def _fetch_detail(self, session: requests.Session, course_id: str, course_type: str) -> str:
        """교육과정 상세 페이지에서 과정소개 텍스트를 추출한다."""
        try:
            # ECR prefix = 협력사(MX) 파트너 교육과정 — 별도 엔드포인트 사용
            if course_id.startswith("ECR"):
                resp = session.get(
                    f"{BASE_URL}/user/learnEcon/ALL/learnPartnerEcondtl",
                    params={"p_conts_sn": course_id},
                    headers={"Referer": f"{BASE_URL}/user/learnEcon/MX/menu/list"},
                    timeout=20,
                )
            else:
                resp = session.post(
                    f"{BASE_URL}/user/learnEcon/ALL/learnEconDtl",
                    data={"p_curculm_sn": course_id, "p_curculm_cat": course_type},
                    headers={"Referer": f"{BASE_URL}/user/learnEcon/{course_type}/menu/list"},
                    timeout=20,
                )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            texts = []
            for tit in soup.select(".eduDtl-intro-tit"):
                txt_div = tit.find_next_sibling("div", class_="eduDtl-intro-txt")
                if txt_div:
                    raw = txt_div.get_text(separator=" ", strip=True)
                    raw = raw.replace("\xa0", " ").strip()
                    raw = re.sub(r"\s{2,}", " ", raw)
                    if raw:
                        label = tit.get_text(strip=True)
                        texts.append(f"[{label}]\n{raw}")

            time.sleep(0.3)
            return "\n\n".join(texts[:3])
        except Exception as e:
            self.stderr.write(f"  상세 조회 실패 ({course_id}): {e}")
            return ""
