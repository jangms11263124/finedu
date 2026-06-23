from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PostViewSet

app_name = 'community'

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = router.urls
