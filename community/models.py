from django.conf import settings
from django.db import models


class Post(models.Model):
    """정보 게시판 글 (인기 게시글)."""

    BOARD_CHOICES = [
        ('free', '자유게시판'),
        ('info', '정보공유'),
        ('qna', '질문답변'),
    ]

    board = models.CharField(
        '게시판', max_length=10, choices=BOARD_CHOICES, default='free'
    )
    title = models.CharField('제목', max_length=200)
    content = models.TextField('내용', blank=True)
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
    """게시글 댓글."""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} - {self.content[:20]}'
