from django.db import models
from books.models import UserBook


class ReadingNote(models.Model):
    user_book = models.ForeignKey(UserBook, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    note_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_book']),
            models.Index(fields=['page_number']),
        ]


