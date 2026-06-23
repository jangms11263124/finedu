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
    list_display = ('title', 'status', 'host', 'start_date', 'end_date')
    list_filter = ('status',)
    search_fields = ('title', 'host')
