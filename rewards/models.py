from django.db import models
from django.conf import settings
from books.models import UserBook


class UserPoint(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points')
    total_points = models.PositiveIntegerField(default=0)
    used_points = models.PositiveIntegerField(default=0)
    available_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_points(self, points, reason):
        self.total_points += points
        self.available_points += points
        self.save()

        PointHistory.objects.create(
            user=self.user,
            points=points,
            transaction_type='earn',
            reason=reason
        )

    def use_points(self, points, reason):
        if self.available_points >= points:
            self.used_points += points
            self.available_points -= points
            self.save()

            PointHistory.objects.create(
                user=self.user,
                points=points,
                transaction_type='use',
                reason=reason
            )
            return True
        return False

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]


class PointHistory(models.Model):
    TRANSACTION_TYPES = [
        ('earn', '적립'),
        ('use', '사용'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]


class CafeCoupon(models.Model):
    COUPON_TYPES = [
        ('americano', '아메리카노'),
        ('latte', '라떼'),
        ('dessert', '디저트'),
    ]

    name = models.CharField(max_length=100)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES)
    required_points = models.PositiveIntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.required_points} 포인트)"


class UserCoupon(models.Model):
    STATUS_CHOICES = [
        ('available', '사용가능'),
        ('used', '사용완료'),
        ('expired', '만료'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(CafeCoupon, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    coupon_code = models.CharField(max_length=20, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['coupon_code']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.coupon.name}"


class ReadingStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_reading_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_streak(self, reading_date):
        from datetime import timedelta

        if self.last_reading_date:
            if reading_date == self.last_reading_date:
                return  # 같은 날은 스킵
            elif reading_date == self.last_reading_date + timedelta(days=1):
                self.current_streak += 1
            else:
                self.current_streak = 1
        else:
            self.current_streak = 1

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_reading_date = reading_date
        self.save()

        # 7일 연속 독서 보너스
        if self.current_streak == 7:
            user_points, created = UserPoint.objects.get_or_create(user=self.user)
            user_points.add_points(30, "7일 연속 독서 보너스")