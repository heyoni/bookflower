from django.db import models
from django.conf import settings


class UserBook(models.Model):
    STATUS_CHOICES = [
        ('reading', '읽는 중'),
        ('completed', '완독'),
        ('paused', '일시정지'),
        ('dropped', '중단'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    external_book_id = models.CharField(max_length=100)
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255, null=True, blank=True)
    total_pages = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reading')
    current_page = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
