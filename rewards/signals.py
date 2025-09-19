from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from books.models import UserBook
from reading.models import ReadingNote
from .services import PointService


@receiver(post_save, sender=UserBook)
def award_completion_points(sender, instance, created, **kwargs):
    """책 완독 시 포인트 적립"""
    if not created and instance.status == 'completed':
        # 이전 상태 확인을 위해 DB에서 다시 조회
        try:
            old_instance = UserBook.objects.get(pk=instance.pk)
            # 완독 상태로 변경된 경우에만 포인트 지급
            if hasattr(old_instance, '_previous_status') and old_instance._previous_status != 'completed':
                PointService.award_book_completion_points(instance.user, instance)
                PointService.update_reading_streak(instance.user)
        except UserBook.DoesNotExist:
            pass


@receiver(pre_save, sender=UserBook)
def store_previous_status(sender, instance, **kwargs):
    """이전 상태 저장"""
    if instance.pk:
        try:
            old_instance = UserBook.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except UserBook.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=ReadingNote)
def award_note_points(sender, instance, created, **kwargs):
    """독서 노트 작성 시 포인트 적립"""
    if created:
        PointService.award_note_points(instance.user_book.user, instance.user_book)
        # 독서 활동으로 연속일 업데이트
        PointService.update_reading_streak(instance.user_book.user)