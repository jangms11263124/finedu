from django.db.models import Count, F
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


class AIRecommendView(APIView):
    """POST /api/contents/ai-recommend/ — RAG 기반 AI 맞춤 콘텐츠 추천.

    body: { ebti?: {...}, region?: "..." }  (EBTI는 프론트 localStorage에서 전달)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ebti = request.data.get('ebti')
        region = request.data.get('region', '')
        result = ai.recommend(request.user, ebti=ebti, region=region)
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
        if q := params.get('q'):
            qs = (qs.filter(title__icontains=q)
                  | qs.filter(summary__icontains=q)).distinct()
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
        if status_ := params.get('status'):
            qs = qs.filter(status=status_)
        if region := params.get('region'):
            qs = qs.filter(region=region)
        if online_type := params.get('online_type'):
            qs = qs.filter(online_type=online_type)
        return qs
