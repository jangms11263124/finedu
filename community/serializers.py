from rest_framework import serializers

from .models import Comment, Post


class PostListSerializer(serializers.ModelSerializer):
    """목록/인기 게시글용 (가벼운 표현)."""

    author = serializers.CharField(source='author.nickname', read_only=True)
    board_display = serializers.CharField(
        source='get_board_display', read_only=True
    )
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'board', 'board_display', 'title', 'author',
                  'views', 'comment_count', 'created_at')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.nickname', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'author_id', 'content', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    """상세 표현."""

    author = serializers.CharField(source='author.nickname', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    board_display = serializers.CharField(
        source='get_board_display', read_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'board', 'board_display', 'title', 'content',
                  'author', 'author_id', 'views', 'comment_count', 'comments',
                  'created_at', 'updated_at')
