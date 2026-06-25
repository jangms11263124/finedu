"""finedu URL 설정. /api/ 하위에 REST 엔드포인트를 둔다."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('contents.urls')),
    path('api/', include('community.urls')),
    path('api/', include('glossary.urls')),
    path('api/', include('quiz.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
