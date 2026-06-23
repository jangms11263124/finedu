from rest_framework import serializers

from .models import Content, ContentComment, Event


class ContentCommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.nickname', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)

    class Meta:
        model = ContentComment
        fields = ('id', 'content', 'author', 'author_id', 'body', 'created_at')
        read_only_fields = ('content',)


class ContentSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ('id', 'title', 'summary', 'body', 'category',
                  'category_display', 'thumbnail', 'views', 'like_count',
                  'comment_count', 'is_liked', 'is_recommended',
                  'is_popular', 'created_at')

    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.likes.filter(pk=user.pk).exists()
        return False


class EventSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Event
        fields = ('id', 'title', 'summary', 'body', 'thumbnail', 'status',
                  'status_display', 'host', 'start_date', 'end_date',
                  'created_at')
