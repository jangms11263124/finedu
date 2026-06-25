from django.db.models import Count, F, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from . import ai
from .models import Content, Event
from .serializers import (
    ContentCommentSerializer,
    ContentSerializer,
    EventSerializer,
)

# EBTI 추천 태그 → 실제 검색어 확장 매핑
# 태그 자체로는 영상 제목에 잘 안 나오므로 유의어·관련어로 OR 검색
EBTI_SYNONYMS = {
    '소비지출관리': ['소비', '지출', '가계부', '통장관리'],
    '소비지출':    ['소비', '지출'],
    '합리적소비':  ['소비', '절약', '지출'],
    '신용관리':    ['신용', '신용점수', '신용등급'],
    '신용카드':    ['신용카드', '카드'],
    '체크카드':    ['체크카드', '체크'],
    '자산관리':    ['자산', '재테크', '돈관리'],
    '포트폴리오':  ['포트폴리오', '분산투자', '자산배분'],
    '예금적금':    ['예금', '적금', '저축'],
    '부채관리':    ['대출', '부채', '빚'],
    '금융상품':    ['금융상품', 'ISA', 'ETF', '연금저축'],
    '기준금리':    ['금리', '기준금리', '이자'],
    '물가':        ['물가', '인플레이션'],
    '환율':        ['환율', '달러', '외환'],
    '정부정책':    ['청약', '정책', '지원금', '청년혜택'],
    '경제전망':    ['경제', '전망', '시황'],
    '팩트체크':    ['경제', '금리', '환율', '물가'],
    '위기관리':    ['비상금', '위기', '대비'],
    '신용위험관리':['신용', '연체', '대출위험'],
    '보이스피싱':  ['보이스피싱', '금융사기', '사기'],
    '소비자보호':  ['소비자', '환불', '소비자권리'],
    '소비자권리':  ['소비자', '권리', '피해구제'],
    '금융사기예방':['금융사기', '사기예방', '보이스피싱'],
    '노후대비':    ['노후', '은퇴', '연금'],
    '노후설계':    ['노후', '재무설계', '은퇴'],
    '연금':        ['연금', 'IRP', '연금저축', '퇴직연금'],
    '보험':        ['보험', '실손', '생명보험'],
    '은퇴자산':    ['은퇴', '노후', '은퇴준비', '노후자금'],
    '생애주기':    ['생애주기', '재무설계', '인생계획', '재테크'],
}


class AIRecommendView(APIView):
    """POST /api/contents/ai-recommend/ — RAG 기반 AI 맞춤 콘텐츠 추천.

    body: { ebti?: {...} }  (EBTI는 프론트 localStorage에서 전달)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ebti = request.data.get('ebti')
        result = ai.recommend(request.user, ebti=ebti)
        return Response(result)


class ContentViewSet(viewsets.ModelViewSet):
    """콘텐츠 CRUD + 커뮤니티 활동(좋아요·댓글)·랭킹."""

    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('recommended') in ('1', 'true'):
            qs = qs.filter(is_recommended=True)
        if params.get('popular') in ('1', 'true'):
            qs = qs.filter(is_popular=True).order_by('-views')
        if category := params.get('category'):
            qs = qs.filter(category=category)
        # 마이페이지: 좋아요한 콘텐츠
        if params.get('liked') == 'me' and self.request.user.is_authenticated:
            qs = qs.filter(likes=self.request.user)
        # 마이페이지: 스크랩한 콘텐츠
        if params.get('scrapped') == 'me' and self.request.user.is_authenticated:
            qs = qs.filter(scraps=self.request.user)
        if q := params.get('q'):
            # EBTI 태그면 유의어로 확장, 아니면 그대로 사용
            terms = EBTI_SYNONYMS.get(q, [q])
            q_filter = Q()
            for term in terms:
                q_filter |= Q(title__icontains=term)
                q_filter |= Q(summary__icontains=term)
                q_filter |= Q(body__icontains=term)
            qs = qs.filter(q_filter).distinct()
        ordering = params.get('ordering')
        if ordering == 'views':
            qs = qs.order_by('-views')
        elif ordering == 'oldest':
            qs = qs.order_by('created_at')
        return qs

    def retrieve(self, request, *args, **kwargs):
        """상세 조회 시 조회수 +1."""
        instance = self.get_object()
        Content.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ranking(self, request):
        """좋아요 순 콘텐츠 랭킹 (커뮤니티 페이지)."""
        qs = (
            Content.objects.annotate(_likes=Count('likes'))
            .order_by('-_likes', '-views')[:10]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """좋아요 토글."""
        content = self.get_object()
        user = request.user
        if content.likes.filter(pk=user.pk).exists():
            content.likes.remove(user)
            liked = False
        else:
            content.likes.add(user)
            liked = True
        return Response({'liked': liked, 'like_count': content.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def scrap(self, request, pk=None):
        """스크랩 토글."""
        content = self.get_object()
        user = request.user
        if content.scraps.filter(pk=user.pk).exists():
            content.scraps.remove(user)
            scrapped = False
        else:
            content.scraps.add(user)
            scrapped = True
        return Response(
            {'scrapped': scrapped, 'scrap_count': content.scraps.count()}
        )

    @action(detail=True, methods=['get', 'post'],
            permission_classes=[IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        """콘텐츠 댓글 목록 조회 / 작성."""
        content = self.get_object()
        if request.method == 'POST':
            serializer = ContentCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(content=content, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        qs = content.comments.select_related('author').all()
        return Response(ContentCommentSerializer(qs, many=True).data)


class EventViewSet(viewsets.ModelViewSet):
    """교육 행사 · 프로그램 CRUD. ?status=open 필터."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        # 마이페이지: 스크랩한 교육 행사
        if params.get('scrapped') == 'me' and self.request.user.is_authenticated:
            qs = qs.filter(scraps=self.request.user)

        if app_status := params.get('app_status'):
            import datetime
            today = datetime.date.today()
            from django.db.models import Q
            if app_status == 'upcoming':
                qs = qs.filter(start_date__gt=today)
            elif app_status == 'ongoing':
                qs = qs.filter(
                    Q(start_date__lte=today) | Q(start_date__isnull=True),
                    Q(end_date__gte=today) | Q(end_date__isnull=True),
                    status='open'
                )
            elif app_status == 'closed':
                qs = qs.filter(
                    Q(end_date__lt=today) | Q(status__in=['closed', 'ended'])
                )
        elif status_ := params.get('status'):
            qs = qs.filter(status=status_)
            
        if region := params.get('region'):
            qs = qs.filter(region=region)
        if online_type := params.get('online_type'):
            qs = qs.filter(online_type=online_type)

        import datetime
        from django.db.models import Case, When, Value, IntegerField, F
        today = datetime.date.today()

        status_priority = Case(
            # ongoing
            When(
                status='open',
                start_date__lte=today,
                end_date__gte=today,
                then=Value(1)
            ),
            When(
                status='open',
                start_date__isnull=True,
                end_date__gte=today,
                then=Value(1)
            ),
            When(
                status='open',
                start_date__lte=today,
                end_date__isnull=True,
                then=Value(1)
            ),
            When(
                status='open',
                start_date__isnull=True,
                end_date__isnull=True,
                then=Value(1)
            ),
            # upcoming
            When(
                start_date__gt=today,
                then=Value(2)
            ),
            # closed (fallback)
            default=Value(3),
            output_field=IntegerField()
        )

        qs = (
            qs.annotate(status_priority=status_priority)
            .order_by('status_priority', F('end_date').asc(nulls_last=True), '-created_at')
        )
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def scrap(self, request, pk=None):
        """교육 행사 스크랩 토글."""
        event = self.get_object()
        user = request.user
        if event.scraps.filter(pk=user.pk).exists():
            event.scraps.remove(user)
            scrapped = False
        else:
            event.scraps.add(user)
            scrapped = True
        return Response(
            {'scrapped': scrapped, 'scrap_count': event.scraps.count()}
        )
