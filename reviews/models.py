from django.db import models
from books.models import UserBook


class BookReview(models.Model):
    user_book = models.ForeignKey(UserBook, on_delete=models.CASCADE)
    review_content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)
