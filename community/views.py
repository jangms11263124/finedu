from django.db.models import F
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Comment, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import CommentSerializer, PostListSerializer, PostSerializer


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


class CommentViewSet(viewsets.ModelViewSet):
    """댓글 CRUD. 생성 시 post id를 body에 담아 전송."""

    queryset = Comment.objects.select_related('author').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
