from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .models import Comment, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import CommentSerializer, PostListSerializer, PostSerializer


def _toggle_like(obj, user):
    """좋아요 토글 후 (liked, like_count) 반환."""
    if obj.likes.filter(pk=user.pk).exists():
        obj.likes.remove(user)
        liked = False
    else:
        obj.likes.add(user)
        liked = True
    return liked, obj.likes.count()


class PostViewSet(viewsets.ModelViewSet):
    """게시글 CRUD. ?popular=1 인기 게시글 / ?board= 게시판 필터."""

    queryset = Post.objects.select_related('author').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('popular') in ('1', 'true'):
            qs = qs.order_by('-views', '-created_at')
        if board := params.get('board'):
            qs = qs.filter(board=board)
        if q := params.get('q'):
            qs = qs.filter(title__icontains=q)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """상세 조회 시 조회수 +1."""
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """게시글 좋아요 토글."""
        liked, count = _toggle_like(self.get_object(), request.user)
        return Response({'liked': liked, 'like_count': count})


class CommentViewSet(viewsets.ModelViewSet):
    """댓글·대댓글 CRUD. 생성 시 post(필수)·parent(대댓글이면) id 전송."""

    queryset = Comment.objects.select_related('author').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """댓글 좋아요 토글."""
        liked, count = _toggle_like(self.get_object(), request.user)
        return Response({'liked': liked, 'like_count': count})
