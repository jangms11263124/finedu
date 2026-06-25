from rest_framework import serializers

from .models import Comment, Post


class _LikeMixin:
    """is_liked 계산 공통 로직."""

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(pk=request.user.pk).exists()
        return False


class PostListSerializer(serializers.ModelSerializer):
    """목록/인기 게시글용 (가벼운 표현)."""

    author = serializers.CharField(source='author.nickname', read_only=True)
    board_display = serializers.CharField(
        source='get_board_display', read_only=True
    )
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'board', 'board_display', 'title', 'author',
                  'views', 'comment_count', 'like_count', 'created_at')


class CommentSerializer(_LikeMixin, serializers.ModelSerializer):
    author = serializers.CharField(source='author.nickname', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post', 'parent', 'author', 'author_id', 'content',
                  'like_count', 'is_liked', 'replies', 'created_at')

    def get_replies(self, obj):
        # 대댓글(자식)을 재귀적으로 직렬화
        return CommentSerializer(
            obj.replies.select_related('author').all(),
            many=True,
            context=self.context,
        ).data


class PostSerializer(_LikeMixin, serializers.ModelSerializer):
    """상세 표현."""

    author = serializers.CharField(source='author.nickname', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    board_display = serializers.CharField(
        source='get_board_display', read_only=True
    )
    comments = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'board', 'board_display', 'title', 'content', 'image',
                  'author', 'author_id', 'views', 'comment_count',
                  'like_count', 'is_liked', 'comments',
                  'created_at', 'updated_at')

    def get_comments(self, obj):
        # 최상위 댓글만 (대댓글은 각 댓글의 replies로 표현)
        top = obj.comments.filter(parent__isnull=True).select_related('author')
        return CommentSerializer(top, many=True, context=self.context).data
