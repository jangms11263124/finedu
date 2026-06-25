"""
유저별 맞춤 활동 더미 데이터 생성 (AI 추천 테스트용)

각 유저의 페르소나:
  finedu_demo  (핀에듀지기)  — 균형형: 소비/변화는 강하나 위기관리·노후 취약
  econ_master  (경제마스터)  — 경제이슈형: 거시경제·환율·금리에 강한 관심
  saving_queen (절약여왕)    — 절약저축형: 저축·가계부 집중, 소비지출 습관 약함
  young_invest (주린이탈출)  — 투자입문형: 주식·ETF 관심, 자산관리·노후 취약
  coin_lover   (코인러버)    — 금융상품형: 보험·금융상품 관심, 위기관리·노후 취약

사용법:
  python manage.py seed_user_activity
  python manage.py seed_user_activity --clear   # 기존 활동 데이터 초기화 후 재생성
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from community.models import Post, Comment
from contents.models import Content, ContentComment
from quiz.models import DailyQuiz, QuizAttempt

User = get_user_model()

# EBTI 점수 템플릿 (spend, asset, change, risk, retire)
EBTI_FEEDBACK = {
    'spend': {
        'name': '소비(지출) 관리',
        'strong_fb': '합리적 소비를 실천하기 위해 꾸준히 노력하고 있어요.',
        'weak_fb': '소비 계획을 세우고 지출을 점검하는 습관이 필요해요. 체크카드 활용과 가계부 작성을 시작해 보세요.',
        'weak_tags': ['소비지출관리', '소비지출', '합리적소비', '신용관리', '신용카드', '체크카드'],
    },
    'asset': {
        'name': '자산 관리',
        'strong_fb': '금융상품을 이해하고 자산을 계획적으로 관리하고 있어요.',
        'weak_fb': '예금·적금부터 시작해 포트폴리오를 단계적으로 구성해 보세요.',
        'weak_tags': ['자산관리', '자산', '저축', '투자', '포트폴리오', '예금적금', '부채관리', '금융상품'],
    },
    'change': {
        'name': '변화 대응',
        'strong_fb': '경제 뉴스와 정책 변화를 꾸준히 파악하며 잘 대응하고 있어요.',
        'weak_fb': '금리·환율·정부 정책 등 경제 환경 변화에 더 관심을 기울여 보세요.',
        'weak_tags': ['경제이슈', '기준금리', '물가', '환율', '정부정책', '경제전망', '팩트체크'],
    },
    'risk': {
        'name': '위기 관리',
        'strong_fb': '금융 사기와 위험 상황에 잘 대비하고 있어요.',
        'weak_fb': '보이스피싱·금융사기 예방, 비상금 마련 등 위기 대비에 신경을 더 써 주세요.',
        'weak_tags': ['위기관리', '신용위험관리', '보이스피싱', '소비자보호', '소비자권리', '금융사기예방'],
    },
    'retire': {
        'name': '노후 대비',
        'strong_fb': '젊은 시절부터 노후를 체계적으로 준비하고 있어요.',
        'weak_fb': '연금·보험 등으로 지금부터 노후를 준비해 보세요. 복리의 힘은 시작이 빠를수록 강해집니다.',
        'weak_tags': ['노후대비', '노후설계', '연금', '보험', '은퇴자산', '생애주기'],
    },
}

PERSONA_MAP = {
    1: {'min': 0, 'emoji': '🌱', 'name': '막 시작한\n경제 새싹', 'desc': '아직 경제 습관이 형성 중이에요.\n작은 것부터 하나씩 챙겨보세요.'},
    2: {'min': 2, 'emoji': '🧭', 'name': '방향을 잡아가는\n경제 탐색자', 'desc': '몇 영역에서 좋은 습관이 있어요.\n보완이 필요한 영역만 조금 더 챙기면 빠르게 성장할 수 있어요.'},
    3: {'min': 3, 'emoji': '💡', 'name': '경제 감각을 키우는\n성장형 인재', 'desc': '꽤 균형잡힌 경제 습관을 갖추고 있어요.\n나머지 영역도 강화하면 완벽해요.'},
    4: {'min': 4, 'emoji': '🏆', 'name': '탄탄한 경제 습관의\n금융 마스터', 'desc': '거의 모든 영역에서 건강한 경제 습관을 갖추고 있어요!\n이 상태를 유지하면 금융 고수가 될 수 있어요.'},
    5: {'min': 5, 'emoji': '👑', 'name': '완벽한 경제 습관의\n파이낸셜 킹', 'desc': '모든 영역에서 훌륭한 경제 습관을 갖추었어요!\n이미 금융 고수입니다.'},
}


def make_ebti(scores: dict) -> dict:
    """scores = {key: int 0~20} → EBTI JSON 구조 생성."""
    THRESHOLD = 14
    breakdown = []
    strong_count = 0
    for key in ['spend', 'asset', 'change', 'risk', 'retire']:
        score = scores[key]
        strong = score >= THRESHOLD
        if strong:
            strong_count += 1
        info = EBTI_FEEDBACK[key]
        breakdown.append({
            'key': key,
            'name': info['name'],
            'score': score,
            'strong': strong,
            'feedback': info['strong_fb'] if strong else info['weak_fb'],
            'tags': [] if strong else info['weak_tags'],
        })

    # 페르소나 선택
    for min_val in sorted(PERSONA_MAP.keys(), reverse=True):
        if strong_count >= min_val:
            persona = PERSONA_MAP[min_val]
            break
    else:
        persona = PERSONA_MAP[1]

    return {
        'breakdown': breakdown,
        'strongCount': strong_count,
        'persona': {'min': strong_count, **persona},
    }


# ── 유저별 페르소나 정의 ───────────────────────────────────────────────────────
USERS = {
    'finedu_demo': {
        'nickname': '핀에듀지기',
        'ebti_scores': {'spend': 20, 'asset': 18, 'change': 17, 'risk': 7, 'retire': 3},
        'like_categories': ['economy', 'saving', 'invest'],  # 고르게
        'like_count': 8,
        'posts': [
            ('info', '사회초년생 첫 월급 관리 어떻게 해야 할까요?',
             '이번 달부터 직장 생활을 시작했어요. 월급이 들어왔는데 어떻게 관리해야 할지 막막합니다. 통장 쪼개기를 해야 한다고 들었는데 어떤 비율로 나눠야 할지 조언 부탁드려요.'),
            ('qna', '연말정산 처음 해보는데 뭐가 뭔지 모르겠어요',
             '회사에서 연말정산 서류 제출하라고 하는데 공제 항목이 너무 많아서 헷갈려요. 사회초년생이 꼭 챙겨야 할 공제 항목이 뭐가 있을까요?'),
        ],
        'comments': [
            '저도 비슷한 고민이었는데 통장 쪼개기 정말 도움 됐어요!',
            '연말정산은 국세청 홈택스에서 자동 채워주는 기능 이용하면 편해요.',
        ],
        'quiz_wrong_topics': ['금리', '세금'],
    },
    'econ_master': {
        'nickname': '경제마스터',
        'ebti_scores': {'spend': 19, 'asset': 18, 'change': 6, 'risk': 17, 'retire': 16},
        'like_categories': ['economy'],
        'like_count': 12,
        'posts': [
            ('info', '미국 기준금리 인하 가능성과 우리 재테크 전략',
             '연준이 금리를 내릴 것 같다는 뉴스가 계속 나오는데, 이게 우리나라 금리와 환율에 어떤 영향을 줄지 분석해봤습니다. 채권·달러·주식 각각 어떤 전략이 좋을지 의견 나눠봐요.'),
            ('free', '환율 1400원 돌파... 지금 달러 사야 할까요?',
             '원달러 환율이 심상치 않네요. 달러 예금이나 달러 ETF를 지금 시점에 사는 게 맞는 전략일까요? 아니면 더 기다려야 할까요?'),
            ('info', '한국 GDP 성장률 전망과 투자 시사점',
             '최근 발표된 경제 지표들을 보면 성장 둔화 신호가 보입니다. 수출 주도 경제에서 이런 변화가 어떤 의미인지, 투자 포트폴리오를 어떻게 조정해야 할지 이야기해봐요.'),
        ],
        'comments': [
            '금리 인하 시기에는 채권 ETF가 유리하다고 생각해요.',
            '환율 리스크 헷지를 위해 환노출 상품과 환헤지 상품을 혼합하는 전략도 고려해보세요.',
            '경제 지표 분석 잘 하셨네요. 저도 비슷한 생각이에요.',
        ],
        'quiz_wrong_topics': ['환율', '경제전망'],
    },
    'saving_queen': {
        'nickname': '절약여왕',
        'ebti_scores': {'spend': 5, 'asset': 15, 'change': 18, 'risk': 19, 'retire': 17},
        'like_categories': ['saving'],
        'like_count': 10,
        'posts': [
            ('review', '6개월 가계부 작성 후기 — 월 50만원 절약 성공!',
             '올해 초부터 가계부를 쓰기 시작했는데 6개월 만에 월 지출을 50만원이나 줄였어요. 제가 사용하는 가계부 앱과 항목 분류 방법을 공유할게요. 특히 구독 서비스 정리만으로도 월 3만원이 절약됐어요!'),
            ('info', '신용카드 vs 체크카드, 사회초년생은 어떤 게 나을까?',
             '신용카드는 포인트 적립이 좋고 체크카드는 연말정산 공제율이 높은데, 저는 체크카드 위주로 사용하면서 소비 습관을 먼저 잡는 게 맞다고 생각해요. 여러분의 생각은?'),
            ('qna', '월급의 몇 %를 저축해야 할까요?',
             '현재 월급의 30%를 저축 중인데 너무 적은 건지 모르겠어요. 사회초년생 평균 저축률이 어느 정도인가요? 더 늘리려면 어디서 줄여야 할지 팁 부탁드려요.'),
        ],
        'comments': [
            '저도 가계부 쓰기 시작했는데 외식비가 생각보다 너무 많이 나오더라고요.',
            '체크카드 연말정산 공제율 30%라 저도 체크카드 위주로 써요!',
            '저축률 50% 도전 중인데 생활비 줄이는 게 쉽지 않네요.',
        ],
        'quiz_wrong_topics': ['소비', '신용카드'],
    },
    'young_invest': {
        'nickname': '주린이탈출',
        'ebti_scores': {'spend': 16, 'asset': 5, 'change': 14, 'risk': 14, 'retire': 4},
        'like_categories': ['invest'],
        'like_count': 12,
        'posts': [
            ('info', '주린이 탈출 1년 후기 — ETF로 수익률 15% 달성',
             '작년 이맘때 처음 주식을 시작했는데 코스피 지수 추종 ETF와 S&P500 ETF 반반 투자로 1년 수익률 15%를 달성했어요. 개별주식 욕심 버리고 ETF에 집중한 게 정답이었던 것 같아요.'),
            ('qna', 'ISA 계좌와 연금저축 중 뭘 먼저 채워야 할까요?',
             '두 계좌 다 세제 혜택이 있다고 하는데 자금이 한정적일 때 어떤 걸 우선해야 하는지 고민이에요. 세금 절약 측면에서 어떤 순서로 투자하는 게 맞을까요?'),
            ('study', '재테크 스터디 모집 — 매주 토요일 오전',
             '같이 재테크 공부할 분들 모집합니다! 주제는 ETF 투자, 포트폴리오 구성, 세금 최적화 등이에요. 초보자도 환영합니다. 카카오톡 오픈채팅으로 연락주세요.'),
        ],
        'comments': [
            '저도 ETF 위주로 투자하는데 맞는 방향인 것 같아요!',
            'ISA 계좌 먼저 꽉 채우고 남는 돈으로 연금저축 넣는 게 일반적으로 맞다고 해요.',
            '분산투자가 진리입니다. 한 종목에 몰빵하면 멘탈이 흔들려요.',
        ],
        'quiz_wrong_topics': ['ETF', '포트폴리오'],
    },
    'coin_lover': {
        'nickname': '코인러버',
        'ebti_scores': {'spend': 15, 'asset': 18, 'change': 17, 'risk': 5, 'retire': 3},
        'like_categories': ['finance', 'society'],
        'like_count': 10,
        'posts': [
            ('info', '보이스피싱 실제 경험담 — 이렇게 당할 뻔했어요',
             '얼마 전 실제로 보이스피싱 전화를 받았어요. 검사 사칭이었는데 처음엔 정말 진짜인 줄 알았어요. 제가 눈치챈 포인트와 신고 방법을 공유할게요. 다들 조심하세요!'),
            ('qna', '실손보험 vs 암보험, 20대에 어떤 걸 먼저 가입해야 할까요?',
             '보험 설계사들이 이것저것 권유하는데 뭘 믿어야 할지 모르겠어요. 20대 사회초년생 입장에서 보험 우선순위가 어떻게 되는지 알려주실 분 있나요?'),
            ('info', '금융감독원 파인(FINE) 사이트 — 금융사기 예방의 필수템',
             '금감원 파인 사이트에서 금융회사 등록 여부 확인, 불법 금융업체 조회 등 다양한 서비스를 무료로 이용할 수 있어요. 특히 보이스피싱·불법 대출 사기 예방에 꼭 필요한 사이트예요.'),
        ],
        'comments': [
            '보이스피싱 전화 끊고 바로 경찰에 신고하는 게 정답이에요.',
            '20대는 실손보험이 최우선이라고 들었어요. 암보험은 30대 이후에 가입해도 늦지 않다고.',
            '금감원 파인 사이트 처음 알았어요. 북마크 해뒀어요!',
        ],
        'quiz_wrong_topics': ['보험', '노후'],
    },
}


class Command(BaseCommand):
    help = '유저별 맞춤 활동 더미 데이터를 생성합니다 (AI 추천 테스트용).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='기존 활동 데이터(좋아요·게시글·댓글·퀴즈응답)를 초기화한 후 재생성',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Post.objects.exclude(author__username='').delete()
            QuizAttempt.objects.all().delete()
            for u in User.objects.all():
                u.liked_contents.clear()
            self.stdout.write('기존 활동 데이터 초기화 완료')

        all_contents = {
            cat: list(Content.objects.filter(category=cat).values_list('id', flat=True))
            for cat in ['invest', 'saving', 'economy', 'finance', 'society']
        }
        quizzes = list(DailyQuiz.objects.all())

        posts_created = []

        for username, cfg in USERS.items():
            user = User.objects.filter(username=username).first()
            if not user:
                self.stderr.write(f'유저 없음: {username}')
                continue

            # 1. EBTI 결과 설정
            user.ebti_result = make_ebti(cfg['ebti_scores'])
            user.nickname = cfg['nickname']
            user.save()

            # 2. 콘텐츠 좋아요 추가
            liked_ids = []
            for cat in cfg['like_categories']:
                ids = all_contents.get(cat, [])
                take = min(cfg['like_count'] // len(cfg['like_categories']), len(ids))
                liked_ids.extend(ids[:take])

            for cid in liked_ids:
                try:
                    content = Content.objects.get(id=cid)
                    content.likes.add(user)
                except Content.DoesNotExist:
                    pass

            # 3. 커뮤니티 게시글 작성
            user_posts = []
            for board, title, body in cfg['posts']:
                p = Post.objects.create(
                    author=user, board=board, title=title, content=body,
                    views=0,
                )
                user_posts.append(p)
                posts_created.append(p)

            safe = username.encode('cp949', errors='replace').decode('cp949')
            self.stdout.write(
                f'  [{safe}] EBTI 저장 | 좋아요 {len(liked_ids)}건 | 게시글 {len(user_posts)}건'
            )

        # 4. 댓글 교차 작성 (다른 유저 게시글에 댓글)
        usernames = list(USERS.keys())
        for i, (username, cfg) in enumerate(USERS.items()):
            user = User.objects.filter(username=username).first()
            if not user:
                continue

            # 다음 유저의 게시글에 댓글 달기
            next_username = usernames[(i + 1) % len(usernames)]
            target_posts = [p for p in posts_created if p.author.username == next_username]

            for j, comment_text in enumerate(cfg['comments']):
                if j < len(target_posts):
                    Comment.objects.create(
                        post=target_posts[j],
                        author=user,
                        content=comment_text,
                    )

        # 5. 퀴즈 응답 (일부 오답 처리)
        wrong_users = {
            'finedu_demo': True,   # 틀림
            'econ_master': True,   # 틀림
            'saving_queen': False, # 맞음
            'young_invest': True,  # 틀림
            'coin_lover': False,   # 맞음
        }
        for username, is_wrong in wrong_users.items():
            user = User.objects.filter(username=username).first()
            if not user or not quizzes:
                continue
            quiz = quizzes[0]
            wrong_idx = (quiz.answer_index + 1) % len(quiz.options)
            selected = wrong_idx if is_wrong else quiz.answer_index
            QuizAttempt.objects.get_or_create(
                user=user, quiz=quiz,
                defaults={
                    'selected_index': selected,
                    'is_correct': not is_wrong,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'\n완료: 게시글 {len(posts_created)}건 | 유저 {len(USERS)}명 활동 데이터 생성'
        ))
