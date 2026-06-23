"""홈페이지 시연용 더미 데이터 생성.

    python manage.py seed_demo
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

import random

from community.models import Post
from contents.models import Content, ContentComment, Event
from glossary.models import Term

User = get_user_model()


class Command(BaseCommand):
    help = '홈페이지 데모용 콘텐츠/행사/게시글 데이터를 생성합니다.'

    def handle(self, *args, **options):
        demo, _ = User.objects.get_or_create(
            username='finedu_demo',
            defaults={'nickname': '핀에듀지기', 'points': 480},
        )
        demo.nickname = '핀에듀지기'
        demo.points = 480
        demo.set_password('finedu1234')
        demo.save()

        # 랭킹용 추가 회원들
        members = [demo]
        roster = [
            ('econ_master', '경제마스터', 1280),
            ('saving_queen', '절약여왕', 1050),
            ('young_invest', '주린이탈출', 760),
            ('coin_lover', '코인러버', 540),
        ]
        for uname, nick, pts in roster:
            u, _ = User.objects.get_or_create(
                username=uname, defaults={'nickname': nick}
            )
            u.nickname = nick
            u.points = pts
            u.set_password('finedu1234')
            u.save()
            members.append(u)

        Content.objects.all().delete()
        Event.objects.all().delete()
        Post.objects.all().delete()

        recommended = [
            ('금리 인상이 내 지갑에 미치는 영향', 'economy'),
            ('월급 관리 첫걸음, 통장 쪼개기', 'saving'),
            ('ETF로 시작하는 분산 투자', 'invest'),
            ('알아두면 쓸모있는 금융상품 비교', 'finance'),
        ]
        for i, (title, cat) in enumerate(recommended):
            Content.objects.create(
                title=title,
                summary='경제 초보를 위한 쉽고 친절한 가이드',
                category=cat,
                views=320 + i * 57,
                is_recommended=True,
            )

        popular = [
            ('주식 차트 보는 법 한 번에 정리', 'invest'),
            ('사회초년생을 위한 연말정산 꿀팁', 'finance'),
            ('비트코인, 지금 알아야 할 것들', 'invest'),
            ('청년 우대형 청약통장 완벽 가이드', 'saving'),
        ]
        for i, (title, cat) in enumerate(popular):
            Content.objects.create(
                title=title,
                summary='지금 가장 많이 읽힌 인기 콘텐츠',
                category=cat,
                views=1500 - i * 130,
                is_popular=True,
            )

        # 콘텐츠 보기 페이지 채우기용 일반 콘텐츠
        more_contents = [
            ('이동현 쇼맨 멜처! 한국은행은 왜 독립적일까?', 'economy'),
            ('재정설계Bee와 함께 푸는 재정 꿀Tip', 'finance'),
            ('인 일자리를 바꾼다면? 달은 여기있습니다', 'society'),
            ('예경TEST 시사용어 석유 카르텔 OPEC, UAE', 'economy'),
            ('지구별 경제탐험 시즌2 - 웹툰 EP07', 'economy'),
            ('초롱이, 동고비 사러 갔다가 현물값 떨어뜨려?!', 'invest'),
            ('슬기로운 금융생활 - 우리 아이들의 든든한 미래', 'finance'),
            ('연말정산 미리보기로 13월의 월급 챙기기', 'finance'),
            ('주식 초보를 위한 분산투자 5원칙', 'invest'),
            ('적금 풍차 돌리기, 정말 이득일까?', 'saving'),
            ('환율은 왜 매일 바뀔까? 5분 정리', 'economy'),
            ('신용점수 올리는 7가지 습관', 'finance'),
        ]
        for i, (title, cat) in enumerate(more_contents):
            Content.objects.create(
                title=title,
                summary='쉽고 재미있게 배우는 경제·금융 콘텐츠',
                category=cat,
                views=50 + i * 23,
                # 캐러셀이 풍성하도록 추천/인기 플래그를 번갈아 부여
                is_recommended=(i % 2 == 0),
                is_popular=(i % 2 == 1),
            )

        # 교육 행사 · 프로그램 (지역/온오프라인/접수기간)
        today = date.today()
        events = [
            ('[용인시] 청년 경제 리더십 캠프', '용인시', '경기도', 'offline', 0),
            ('[경기도] 2026 핀테크 실무 인재 양성 과정', '경기도', '경기도', 'both', 1),
            ('[김포시] 배달 노동자 안전교육 및 금융설계 기초', '김포시', '경기도', 'offline', 2),
            ('2024 경기 기술학교 「드론 및 데이터 분석 과정」', '경기도', '경기도', 'offline', 2),
            ('[경기도] 2024 경기청년 글로벌 경제 특사단', '경기도', '경기도', 'online', 2),
            ('2024년 경기 기술학교 「AICE BASIC 취득 과정」', '경기도', '경기도', 'both', 2),
            ('대졸 미취업자를 위한 하이테크 과정 교육생 모집', '한국기술교육원', '대전', 'offline', 5),
            ('[수원시] 하반기 소상공인 마케팅 지원 사업 설명회', '수원시', '경기도', 'offline', 8),
            ('청소년 경제 캠프 2025 여름 특강', '한국금융교육원', '서울', 'offline', 10),
            ('사회초년생 자산관리 온라인 클래스', '핀에듀 아카데미', '온라인', 'online', 12),
            ('금융 데이터로 보는 경제 트렌드 세미나', '서울경제연구소', '서울', 'both', 14),
            ('시니어를 위한 노후 자산 설계 워크숍', '국민연금공단', '부산', 'offline', 16),
            ('대학생 모의 주식 투자 대회', '한국거래소', '서울', 'online', 18),
            ('우리 동네 금융 사기 예방 교실', '금융감독원', '인천', 'offline', 20),
        ]
        for i, (title, host, region, online, dday) in enumerate(events):
            Event.objects.create(
                title=title,
                summary='실생활에 바로 쓰는 금융 지식을 배워보세요.',
                host=host,
                region=region,
                online_type=online,
                status='open' if dday >= 0 else 'closed',
                start_date=today,
                end_date=today + timedelta(days=dday),
            )

        posts = [
            '사회초년생인데 적금 추천 좀 부탁드려요',
            '신용점수 빠르게 올리는 방법 공유합니다',
            '월 50만원 투자 포트폴리오 점검 부탁',
            '연말정산 환급 많이 받는 팁 정리',
            '신용카드 vs 체크카드 뭐가 이득일까요?',
        ]
        for i, title in enumerate(posts):
            Post.objects.create(
                board='info' if i % 2 else 'free',
                title=title,
                content='본문 내용입니다. 다양한 의견을 나눠주세요!',
                author=demo,
                views=900 - i * 110,
            )

        # 모든 콘텐츠에 유튜브 영상 연결 (데모용 공개 영상 ID 순환)
        yt_ids = ['jNQXAC9IVRw', 'aqz-KE-bpKQ', 'dQw4w9WgXcQ', 'YE7VzlLtp-4']
        for i, content in enumerate(Content.objects.all()):
            content.youtube_id = yt_ids[i % len(yt_ids)]
            content.body = (
                content.body
                or '이 영상에서는 ' + content.title + '에 대해 쉽고 자세하게 알아봅니다. '
                '경제·금융 초보자도 부담 없이 따라올 수 있도록 핵심만 짚어드려요.'
            )
            content.save(update_fields=['youtube_id', 'body'])

        # 좋아요 · 콘텐츠 댓글 (커뮤니티 랭킹용)
        comment_samples = [
            '정말 도움이 됐어요!', '쉽게 설명해줘서 좋네요 👍',
            '이거 보고 바로 실천했습니다', '다음 편도 기대할게요',
            '초보한테 딱이에요',
        ]
        all_contents = list(Content.objects.all())
        for content in all_contents:
            likers = random.sample(members, k=random.randint(1, len(members)))
            content.likes.add(*likers)
            for _ in range(random.randint(0, 3)):
                ContentComment.objects.create(
                    content=content,
                    author=random.choice(members),
                    body=random.choice(comment_samples),
                )

        # 경제 용어 사전
        Term.objects.all().delete()
        terms = [
            ('society', '0.5인 가구', '싱글족 가구의 한 유형으로, 한 명이 거주하지만 생활 방식이나 소비 행태는 1인 가구와 다른 형태를 보이는 가구를 이르는 말.'),
            ('management', '1인 창조기업', '개인이 사장이면서 직원인 기업을 의미한다. 창의적인 아이디어, 기술, 전문성 등을 바탕으로 새로운 서비스를 제공한다.'),
            ('economy', '1인당 국민소득', '국민이 일정 기간 동안 벌어들인 소득을 인구수로 나눈 값. 한 나라 국민의 평균적인 소득 수준을 보여주는 대표 지표다.'),
            ('science', '20-20-20 계획', '유럽연합(EU)이 추진한 온실가스·에너지 효율·재생에너지 관련 기후·에너지 통합 목표 계획.'),
            ('finance', '2차 시장', '이미 발행된 증권이 투자자들 사이에서 거래되는 시장. 유통시장이라고도 하며 주식·채권 거래가 이뤄진다.'),
            ('economy', '가산금리', '기준금리에 신용도 등의 조건에 따라 덧붙이는 금리. 위험이 클수록 가산금리가 높아진다.'),
            ('economy', '경기순환', '경제가 호황과 불황을 주기적으로 반복하는 현상. 확장·후퇴·수축·회복의 국면을 거친다.'),
            ('finance', '공매도', '주가 하락이 예상될 때 주식을 빌려서 판 뒤, 가격이 내리면 되사서 갚아 차익을 얻는 투자 기법.'),
            ('economy', '기준금리', '한 나라의 중앙은행이 금융기관과 거래할 때 기준이 되는 정책 금리. 시중 금리의 기준이 된다.'),
            ('finance', '내부자 거래', '기업 내부 정보를 이용해 주식을 거래하여 부당 이득을 취하는 불공정 거래 행위.'),
            ('economy', '디플레이션', '물가가 지속적으로 하락하는 현상. 소비·투자 위축으로 경기 침체를 부를 수 있다.'),
            ('economy', '레버리지', '타인 자본(부채)을 지렛대 삼아 자기자본 수익률을 높이는 투자 전략.'),
            ('society', '리쇼어링', '해외에 진출한 기업이 본국으로 다시 돌아오는 현상.'),
            ('economy', '명목금리', '물가 상승률을 반영하지 않은 표면상의 금리. 실질금리와 구분된다.'),
            ('finance', '뮤추얼펀드', '다수 투자자의 자금을 모아 운용하고 그 수익을 투자자에게 배분하는 회사형 투자신탁.'),
            ('economy', '베이시스 포인트', '금리나 수익률을 나타내는 단위로 0.01%p를 1bp라고 한다.'),
            ('finance', '분산투자', '여러 자산에 나누어 투자해 위험을 줄이는 투자 방법.'),
            ('economy', '스태그플레이션', '경기 침체 속에서 물가가 함께 오르는 현상.'),
            ('management', '스톡옵션', '회사가 임직원에게 일정 가격에 자사 주식을 살 수 있도록 부여하는 권리.'),
            ('economy', '양적완화', '중앙은행이 국채 등을 매입해 시중에 돈을 푸는 통화 정책.'),
            ('finance', 'ETF', '특정 지수를 추종하며 주식처럼 거래소에서 사고팔 수 있는 상장지수펀드.'),
            ('economy', '인플레이션', '물가가 지속적으로 오르는 현상. 화폐 가치가 떨어진다.'),
            ('finance', '자기자본비율', '기업의 총자본 중 자기자본이 차지하는 비율. 재무 건전성을 나타낸다.'),
            ('economy', '잠재성장률', '한 나라가 물가를 자극하지 않으면서 달성할 수 있는 최대 성장률.'),
            ('science', '체리피킹', '자신에게 유리한 것만 골라 취하는 행위를 비유하는 말.'),
            ('finance', '콜옵션', '정해진 가격에 자산을 살 수 있는 권리.'),
            ('economy', '테이퍼링', '중앙은행이 양적완화 규모를 점진적으로 축소하는 것.'),
            ('finance', '파생상품', '주식·채권 등 기초자산의 가치 변동에 따라 가격이 정해지는 금융상품.'),
            ('economy', '한계소비성향', '추가 소득 중 소비로 지출되는 비율.'),
            ('society', 'BTI', '금융 성향을 유형화한 지표로, 소비·자산·위기 관리 등을 진단한다.'),
        ]
        for subject, term, desc in terms:
            Term.objects.create(subject=subject, term=term, description=desc)

        self.stdout.write(self.style.SUCCESS(
            '시드 완료: 회원 %d, 콘텐츠 %d, 행사 %d, 게시글 %d, 콘텐츠댓글 %d, 용어 %d '
            '(demo 계정: finedu_demo / finedu1234)'
            % (User.objects.count(), Content.objects.count(), Event.objects.count(),
               Post.objects.count(), ContentComment.objects.count(), Term.objects.count())
        ))
