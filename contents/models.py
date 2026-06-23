from django.conf import settings
from django.db import models


class Content(models.Model):
    """경제/금융 교육 콘텐츠 (추천 콘텐츠 · 인기 콘텐츠)."""

    CATEGORY_CHOICES = [
        ('economy', '경제'),
        ('invest', '투자'),
        ('saving', '저축'),
        ('finance', '금융상품'),
        ('etc', '기타'),
    ]

    title = models.CharField('제목', max_length=200)
    summary = models.CharField('요약', max_length=300, blank=True)
    body = models.TextField('본문', blank=True)
    category = models.CharField(
        '카테고리', max_length=20, choices=CATEGORY_CHOICES, default='economy'
    )
    thumbnail = models.ImageField(
        '썸네일', upload_to='contents/', blank=True, null=True
    )
    views = models.PositiveIntegerField('조회수', default=0)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_contents',
        blank=True,
        verbose_name='좋아요',
    )
    is_recommended = models.BooleanField('추천 콘텐츠', default=False)
    is_popular = models.BooleanField('인기 콘텐츠', default=False)
    created_at = models.DateTimeField('작성일', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class ContentComment(models.Model):
    """콘텐츠에 달리는 댓글 (커뮤니티 활동)."""

    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_comments',
    )
    body = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} - {self.body[:20]}'


class Event(models.Model):
    """교육 행사 · 프로그램."""

    STATUS_CHOICES = [
        ('open', '모집중'),
        ('closed', '모집마감'),
        ('ended', '종료'),
    ]

    title = models.CharField('제목', max_length=200)
    summary = models.CharField('요약', max_length=300, blank=True)
    body = models.TextField('본문', blank=True)
    thumbnail = models.ImageField(
        '썸네일', upload_to='events/', blank=True, null=True
    )
    status = models.CharField(
        '상태', max_length=10, choices=STATUS_CHOICES, default='open'
    )
    host = models.CharField('주최', max_length=100, blank=True)
    start_date = models.DateField('시작일', blank=True, null=True)
    end_date = models.DateField('종료일', blank=True, null=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
