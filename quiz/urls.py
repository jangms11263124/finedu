from django.urls import path

from .views import TodayQuizView

app_name = 'quiz'

urlpatterns = [
    path('quiz/today/', TodayQuizView.as_view(), name='today'),
]
