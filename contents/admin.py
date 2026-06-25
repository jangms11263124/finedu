from django.contrib import admin

from .models import Content, ContentComment, Event


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'views', 'is_recommended',
                    'is_popular', 'created_at')
    list_filter = ('category', 'is_recommended', 'is_popular')
    search_fields = ('title', 'summary')


@admin.register(ContentComment)
class ContentCommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'created_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'online_type', 'region', 'host',
                    'start_date', 'end_date', 'has_coords')
    list_filter = ('status', 'online_type', 'region')
    search_fields = ('title', 'host', 'place_name', 'address')
    list_editable = ('online_type', 'region')
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'summary', 'body', 'thumbnail',
                       'status', 'host', 'start_date', 'end_date'),
        }),
        ('진행 방식 & 지역', {
            'fields': ('online_type', 'region'),
        }),
        ('장소 & 지도 좌표 (오프라인)', {
            'fields': ('place_name', 'address', 'latitude', 'longitude'),
            'description': '위도/경도는 카카오맵(map.kakao.com)에서 우클릭 → "이 위치로 지도 링크" 또는 좌표 복사로 확인할 수 있습니다.',
        }),
    )

    @admin.display(description='좌표', boolean=True)
    def has_coords(self, obj):
        return bool(obj.latitude and obj.longitude)
