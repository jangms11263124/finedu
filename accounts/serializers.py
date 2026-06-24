from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """프로필 카드 등에서 사용하는 회원 정보."""

    post_count = serializers.SerializerMethodField()
    liked_post_count = serializers.SerializerMethodField()
    liked_content_count = serializers.SerializerMethodField()
    attendance_streak = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'profile_image',
                  'region', 'ebti_result',
                  'post_count', 'liked_post_count', 'liked_content_count',
                  'attendance_streak')

    def get_post_count(self, obj):
        return obj.posts.count()

    def get_liked_post_count(self, obj):
        return obj.liked_posts.count()

    def get_liked_content_count(self, obj):
        return obj.liked_contents.count()

    def get_attendance_streak(self, obj):
        """오늘(또는 어제)부터 거슬러 연속 출석한 일수."""
        from datetime import date, timedelta

        dates = set(obj.attendances.values_list('date', flat=True))
        if not dates:
            return 0
        today = date.today()
        cur = today if today in dates else today - timedelta(days=1)
        streak = 0
        while cur in dates:
            streak += 1
            cur -= timedelta(days=1)
        return streak


class RegisterSerializer(serializers.ModelSerializer):
    """회원가입."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password2': '비밀번호가 일치하지 않습니다.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        if not user.nickname:
            user.nickname = user.username
        user.set_password(password)
        user.save()
        return user
