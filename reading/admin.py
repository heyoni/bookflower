from django.contrib import admin
from .models import ReadingSession, Note


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'pages_read', 'earned_points', 'completed', 'created_at')
    list_filter = ('completed', 'created_at', 'earned_points')
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'page_until', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'book__title', 'note')
    raw_id_fields = ('user', 'book')
