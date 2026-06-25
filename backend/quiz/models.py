from django.conf import settings
from django.db import models


class DailyQuiz(models.Model):
    """날짜별 1개 — AI가 매일 생성하는 경제·금융 상식 퀴즈."""

    date = models.DateField('출제일', unique=True)
    question = models.CharField('문제', max_length=300)
    options = models.JSONField('보기')  # list[str]
    answer_index = models.PositiveSmallIntegerField('정답 번호')  # 0-based
    explanation = models.CharField('해설', max_length=500, blank=True)
    source = models.CharField('생성 출처', max_length=10, default='ai')  # ai|fallback
    created_at = models.DateTimeField('생성일', auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = '오늘의 퀴즈'
        verbose_name_plural = '오늘의 퀴즈'

    def __str__(self):
        return f'[{self.date}] {self.question}'


class QuizAttempt(models.Model):
    """사용자의 하루치 퀴즈 응답 (퀴즈당 1회)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
    )
    quiz = models.ForeignKey(
        DailyQuiz, on_delete=models.CASCADE, related_name='attempts'
    )
    selected_index = models.PositiveSmallIntegerField('선택 번호')
    is_correct = models.BooleanField('정답 여부')
    created_at = models.DateTimeField('응답일시', auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')
        ordering = ['-created_at']

    def __str__(self):
        mark = 'O' if self.is_correct else 'X'
        return f'{self.user} · {self.quiz.date} [{mark}]'


class Attendance(models.Model):
    """사용자 출석 (퀴즈 위젯 조회·응답 시 하루 1회 기록)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    date = models.DateField('출석일')
    created_at = models.DateTimeField('기록일시', auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user} · {self.date}'
