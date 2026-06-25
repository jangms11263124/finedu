from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AIRecommendView, ContentViewSet, EventViewSet

app_name = 'contents'

router = DefaultRouter()
router.register('contents', ContentViewSet, basename='content')
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('contents/ai-recommend/', AIRecommendView.as_view(), name='ai-recommend'),
    *router.urls,
]
