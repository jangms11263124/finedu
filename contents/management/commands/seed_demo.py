"""홈페이지 시연용 더미 데이터 생성.

    python manage.py seed_demo
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

import random

from community.models import Post
from contents.models import Content, ContentComment, Event

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

        events = [
            ('청소년 경제 캠프 2025 여름 특강', '한국금융교육원', 'open'),
            ('사회초년생 자산관리 클래스', '핀에듀 아카데미', 'open'),
            ('금융 데이터로 보는 경제 트렌드 세미나', '서울경제연구소', 'closed'),
        ]
        today = date.today()
        for i, (title, host, status) in enumerate(events):
            Event.objects.create(
                title=title,
                summary='실생활에 바로 쓰는 금융 지식을 배워보세요.',
                host=host,
                status=status,
                start_date=today + timedelta(days=7 + i * 3),
                end_date=today + timedelta(days=14 + i * 3),
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

        self.stdout.write(self.style.SUCCESS(
            '시드 완료: 회원 %d, 콘텐츠 %d, 행사 %d, 게시글 %d, 콘텐츠댓글 %d '
            '(demo 계정: finedu_demo / finedu1234)'
            % (User.objects.count(), Content.objects.count(), Event.objects.count(),
               Post.objects.count(), ContentComment.objects.count())
        ))
