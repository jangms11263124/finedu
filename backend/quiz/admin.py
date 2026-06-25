from django.contrib import admin

from .models import Attendance, DailyQuiz, QuizAttempt


@admin.register(DailyQuiz)
class DailyQuizAdmin(admin.ModelAdmin):
    list_display = ('date', 'question', 'answer_index', 'source')
    list_filter = ('source',)
    ordering = ('-date',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'selected_index', 'is_correct', 'created_at')
    list_filter = ('is_correct',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'created_at')
