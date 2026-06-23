from rest_framework.routers import DefaultRouter

from .views import ContentViewSet, EventViewSet

app_name = 'contents'

router = DefaultRouter()
router.register('contents', ContentViewSet, basename='content')
router.register('events', EventViewSet, basename='event')

urlpatterns = router.urls
