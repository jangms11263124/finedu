from django.conf import settings
from django.db import models


class Post(models.Model):
    """정보 게시판 글 (인기 게시글)."""

    BOARD_CHOICES = [
        ('notice', '공지'),
        ('free', '자유게시판'),
        ('review', '후기게시판'),
        ('info', '정보게시판'),
        ('qna', '질문게시판'),
        ('study', '스터디 모집'),
    ]

    board = models.CharField(
        '게시판', max_length=10, choices=BOARD_CHOICES, default='free'
    )
    title = models.CharField('제목', max_length=200)
    content = models.TextField('내용', blank=True)
    image = models.ImageField('이미지', upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='작성자',
    )
    views = models.PositiveIntegerField('조회수', default=0)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True,
        verbose_name='좋아요',
    )
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def like_count(self):
        return self.likes.count()


class Comment(models.Model):
    """게시글 댓글 + 대댓글(parent)."""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        verbose_name='상위 댓글',
    )
    content = models.TextField('내용')
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True,
        verbose_name='좋아요',
    )
    created_at = models.DateTimeField('작성일', auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} - {self.content[:20]}'

    @property
    def like_count(self):
        return self.likes.count()
