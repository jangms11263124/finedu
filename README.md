# finedu 💰

경제·금융 교육 플랫폼. **Django REST Framework** 백엔드 + **Vue 3 (Vite)** 프론트엔드로 구성된 RESTful 웹 앱입니다.

## 기술 스택

| 영역 | 스택 |
| --- | --- |
| Backend | Django 5.2, Django REST Framework, SimpleJWT, django-cors-headers |
| Frontend | Vue 3, Vue Router, Pinia, Axios, Vite |
| DB | SQLite (개발용) |

## 프로젝트 구조

```
Final_PJT/
├─ finedu/          # Django 프로젝트 설정
├─ accounts/        # 회원 (커스텀 User, JWT 로그인/회원가입)
├─ contents/        # 콘텐츠(추천·인기) + 교육 행사
├─ community/       # 정보 게시판 (게시글·댓글)
├─ manage.py
├─ requirements.txt
└─ frontend/        # Vue 3 SPA
   └─ src/
      ├─ api/         # axios 인스턴스
      ├─ stores/      # pinia (auth)
      ├─ router/
      ├─ components/  # 레이아웃 + 홈 섹션/사이드바 위젯
      └─ views/       # Home / Login / Signup
```

## 실행 방법

### 1. 백엔드 (Django)

```bash
# 가상환경 활성화
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # 홈페이지 데모 데이터 생성
python manage.py runserver      # http://127.0.0.1:8000
```

데모 계정: **finedu_demo / finedu1234**

### 2. 프론트엔드 (Vue)

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

## 주요 API 엔드포인트

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | `/api/accounts/register/` | 회원가입 |
| POST | `/api/accounts/login/` | JWT 로그인 |
| GET | `/api/accounts/me/` | 내 정보 |
| GET | `/api/contents/?recommended=1` | 추천 콘텐츠 |
| GET | `/api/contents/?popular=1` | 인기 콘텐츠 |
| GET | `/api/events/` | 교육 행사·프로그램 |
| GET | `/api/posts/?popular=1` | 인기 게시글 |
| GET | `/api/contents/?page=1&q=&category=&ordering=` | 콘텐츠 목록(검색·정렬·페이지) |
| GET | `/api/events/?page=1&region=&online_type=` | 교육 행사(지역·온오프라인 필터) |
| GET | `/api/terms/?page=1&subject=&initial=&q=` | 경제 용어 사전(주제·두문자·검색) |
| GET | `/api/contents/ranking/` | 커뮤니티 - 콘텐츠 좋아요 랭킹 |
| GET | `/api/accounts/ranking/` | 커뮤니티 - 사용자 활동 랭킹 |
| POST | `/api/contents/{id}/like/` | 콘텐츠 좋아요 토글 |
| GET·POST | `/api/contents/{id}/comments/` | 콘텐츠 댓글 조회·작성 |

## 구현 현황

- [x] 홈페이지 (히어로 · 추천/인기 콘텐츠 · 교육 행사 · 인기 게시글 · 사이드바)
- [x] 로그인 / 회원가입 (JWT)
- [x] 커뮤니티 (콘텐츠 좋아요 랭킹 · 사용자 랭킹 · 좋아요 토글 · 콘텐츠 댓글 API)
- [ ] 콘텐츠 상세 화면 (예정)
