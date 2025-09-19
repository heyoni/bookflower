from django.db import models
from django.conf import settings
from books.models import UserBook


class AIChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_book = models.ForeignKey(UserBook, on_delete=models.CASCADE, null=True, blank=True)
    session_title = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AIChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', '사용자'),
        ('assistant', 'AI 어시스턴트'),
    ]

    chat_session = models.ForeignKey(AIChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['chat_session']),
        ]


class BookReview(models.Model):
    user_book = models.OneToOneField(UserBook, on_delete=models.CASCADE, related_name='ai_review')
    rating = models.PositiveIntegerField(choices=[(i, f'{i}점') for i in range(1, 6)])
    liked_point = models.TextField(blank=True, null=True)
    disliked_point = models.TextField(blank=True, null=True)
    review_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_book']),
        ]
