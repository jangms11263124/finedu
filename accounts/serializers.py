from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """프로필 카드 등에서 사용하는 회원 정보."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'profile_image',
                  'region', 'ebti_result')


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
