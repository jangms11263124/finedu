from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """finedu 회원. 기본 인증 필드 + 닉네임/프로필/포인트(레벨)."""

    nickname = models.CharField('닉네임', max_length=30, blank=True)
    profile_image = models.ImageField(
        '프로필 이미지', upload_to='profiles/', blank=True, null=True
    )
    points = models.PositiveIntegerField('포인트', default=0)

    def __str__(self):
        return self.nickname or self.username

    @property
    def level(self):
        """포인트 기반 간단 레벨 (100점당 1레벨)."""
        return self.points // 100 + 1
