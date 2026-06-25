from datetime import date, timedelta

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import ai
from .models import Attendance, DailyQuiz, QuizAttempt


def _get_or_create_today():
    """오늘의 퀴즈를 가져오고, 없으면 AI로 생성해 저장."""
    today = date.today()
    quiz = DailyQuiz.objects.filter(date=today).first()
    if quiz:
        return quiz
    data = ai.generate_quiz(today)
    # 동시 요청 경합 대비: get_or_create 로 한 건만 생성
    quiz, _ = DailyQuiz.objects.get_or_create(
        date=today,
        defaults={
            'question': data['question'],
            'options': data['options'],
            'answer_index': data['answer_index'],
            'explanation': data['explanation'],
            'source': data['source'],
        },
    )
    return quiz


def _streak(dates, end):
    """end 날짜부터 하루씩 거슬러 연속으로 존재하는 날 수."""
    days = set(dates)
    s = 0
    d = end
    while d in days:
        s += 1
        d -= timedelta(days=1)
    return s


def _streaks(user, today, answered_today, correct_today):
    """(출석 연속일, 정답 연속일) 계산."""
    att_dates = user.attendances.values_list('date', flat=True)
    attendance_streak = _streak(att_dates, today)

    correct_dates = user.quiz_attempts.filter(is_correct=True).values_list(
        'quiz__date', flat=True
    )
    if correct_today:
        correct_streak = _streak(correct_dates, today)
    elif not answered_today:
        # 아직 오늘 안 풀었으면 어제까지의 연속 정답 흐름을 보여준다
        correct_streak = _streak(correct_dates, today - timedelta(days=1))
    else:
        correct_streak = 0  # 오늘 틀림 → 정답 연속 끊김
    return attendance_streak, correct_streak


class TodayQuizView(APIView):
    """오늘의 AI 퀴즈 조회/응답.

    GET  /api/quiz/today/  — 문제 + (로그인 시) 내 응답 상태·스트릭. 출석 기록.
    POST /api/quiz/today/  — body {selected_index} 정답 채점·스트릭 반환.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        quiz = _get_or_create_today()
        today = date.today()
        payload = {
            'date': quiz.date,
            'question': quiz.question,
            'options': quiz.options,
            'authenticated': request.user.is_authenticated,
            'answered': False,
            'selected_index': None,
            'is_correct': None,
            'answer_index': None,
            'explanation': '',
            'attendance_streak': 0,
            'correct_streak': 0,
        }
        if request.user.is_authenticated:
            # 출석 기록 (하루 1회)
            Attendance.objects.get_or_create(user=request.user, date=today)
            attempt = QuizAttempt.objects.filter(
                user=request.user, quiz=quiz
            ).first()
            answered = attempt is not None
            correct_today = bool(attempt and attempt.is_correct)
            att, cor = _streaks(request.user, today, answered, correct_today)
            payload['attendance_streak'] = att
            payload['correct_streak'] = cor
            if attempt:
                payload.update({
                    'answered': True,
                    'selected_index': attempt.selected_index,
                    'is_correct': attempt.is_correct,
                    'answer_index': quiz.answer_index,
                    'explanation': quiz.explanation,
                })
        return Response(payload)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': '로그인이 필요해요.'}, status=401)

        quiz = _get_or_create_today()
        today = date.today()
        try:
            selected = int(request.data.get('selected_index'))
        except (TypeError, ValueError):
            return Response({'detail': '선택이 올바르지 않아요.'}, status=400)
        if not (0 <= selected < len(quiz.options)):
            return Response({'detail': '선택이 올바르지 않아요.'}, status=400)

        Attendance.objects.get_or_create(user=request.user, date=today)
        is_correct = selected == quiz.answer_index
        attempt, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'selected_index': selected, 'is_correct': is_correct},
        )

        # 이미 푼 경우 기존 기록 기준으로 응답
        att, cor = _streaks(
            request.user, today, answered_today=True,
            correct_today=attempt.is_correct,
        )
        return Response({
            'answered': True,
            'selected_index': attempt.selected_index,
            'is_correct': attempt.is_correct,
            'answer_index': quiz.answer_index,
            'explanation': quiz.explanation,
            'attendance_streak': att,
            'correct_streak': cor,
            'already_answered': not created,
        })
