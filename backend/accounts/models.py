from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """finedu 회원. 기본 인증 필드 + 닉네임/프로필."""

    nickname = models.CharField('닉네임', max_length=30, blank=True)
    profile_image = models.ImageField(
        '프로필 이미지', upload_to='profiles/', blank=True, null=True
    )
    region = models.CharField('지역', max_length=30, blank=True)
    ebti_result = models.JSONField('EBTI 결과', blank=True, null=True)

    def __str__(self):
        return self.nickname or self.username
