from datetime import datetime, timedelta
import random
import string
from django.utils import timezone
from .models import UserPoint, ReadingStreak, CafeCoupon, UserCoupon, PointHistory
from reading.models import ReadingNote


class PointService:
    @staticmethod
    def award_book_completion_points(user, user_book):
        """책 완독 시 포인트 적립"""
        user_points, created = UserPoint.objects.get_or_create(user=user)

        # 기본 완독 포인트
        base_points = 100

        # 페이지 수 보너스 (300페이지 이상)
        page_bonus = 50 if user_book.total_pages >= 300 else 0

        # 독서 노트 보너스 계산
        note_count = ReadingNote.objects.filter(user_book=user_book).count()
        note_bonus = min(note_count * 2, 50)  # 최대 50포인트

        total_points = base_points + page_bonus + note_bonus

        reason_parts = [f"'{user_book.book_title}' 완독"]
        if page_bonus > 0:
            reason_parts.append(f"페이지 보너스(+{page_bonus})")
        if note_bonus > 0:
            reason_parts.append(f"독서노트 보너스(+{note_bonus})")

        reason = f"{' '.join(reason_parts)} - 총 {total_points}포인트"

        user_points.add_points(total_points, reason)
        return total_points

    @staticmethod
    def update_reading_streak(user, reading_date=None):
        """독서 연속일 업데이트"""
        if reading_date is None:
            reading_date = timezone.now().date()

        streak, created = ReadingStreak.objects.get_or_create(user=user)
        streak.update_streak(reading_date)
        return streak.current_streak

    @staticmethod
    def award_note_points(user, user_book):
        """독서 노트 작성 시 포인트 적립 (실시간)"""
        user_points, created = UserPoint.objects.get_or_create(user=user)

        # 해당 책의 노트 작성으로 이미 받은 포인트 확인
        existing_note_points = PointHistory.objects.filter(
            user=user,
            reason__contains=f"'{user_book.book_title}' 독서노트"
        ).count() * 2

        # 최대 50포인트까지만 지급
        if existing_note_points < 50:
            user_points.add_points(2, f"'{user_book.book_title}' 독서노트 작성")
            return True
        return False


class CouponService:
    @staticmethod
    def generate_coupon_code():
        """쿠폰 코드 생성"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    @staticmethod
    def exchange_points_for_coupon(user, coupon_id):
        """포인트로 쿠폰 교환"""
        try:
            user_points = UserPoint.objects.get(user=user)
            coupon = CafeCoupon.objects.get(id=coupon_id, is_active=True)

            if user_points.available_points >= coupon.required_points:
                # 포인트 차감
                if user_points.use_points(coupon.required_points, f"{coupon.name} 쿠폰 교환"):
                    # 쿠폰 발급
                    user_coupon = UserCoupon.objects.create(
                        user=user,
                        coupon=coupon,
                        coupon_code=CouponService.generate_coupon_code(),
                        expires_at=timezone.now() + timedelta(days=30)  # 30일 유효
                    )
                    return user_coupon
            return None
        except (UserPoint.DoesNotExist, CafeCoupon.DoesNotExist):
            return None

    @staticmethod
    def use_coupon(coupon_code):
        """쿠폰 사용"""
        try:
            user_coupon = UserCoupon.objects.get(
                coupon_code=coupon_code,
                status='available'
            )

            # 만료 확인
            if user_coupon.expires_at < timezone.now():
                user_coupon.status = 'expired'
                user_coupon.save()
                return False, "쿠폰이 만료되었습니다."

            # 쿠폰 사용 처리
            user_coupon.status = 'used'
            user_coupon.used_at = timezone.now()
            user_coupon.save()

            return True, "쿠폰이 성공적으로 사용되었습니다."

        except UserCoupon.DoesNotExist:
            return False, "유효하지 않은 쿠폰 코드입니다."