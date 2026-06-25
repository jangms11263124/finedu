from django.contrib import admin

from .models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'subject', 'initial', 'created_at')
    list_filter = ('subject', 'initial')
    search_fields = ('term', 'description')
