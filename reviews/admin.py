from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'generated_by_ai', 'created_at')
    list_filter = ('generated_by_ai', 'created_at')
    search_fields = ('user__username', 'book__title', 'content')
    raw_id_fields = ('user', 'book')
