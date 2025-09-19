from django.contrib import admin
from .models import UserPoint, PointHistory, CafeCoupon, UserCoupon, ReadingStreak


@admin.register(UserPoint)
class UserPointAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'available_points', 'used_points', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__nickname']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PointHistory)
class PointHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']


@admin.register(CafeCoupon)
class CafeCouponAdmin(admin.ModelAdmin):
    list_display = ['name', 'coupon_type', 'required_points', 'is_active', 'created_at']
    list_filter = ['coupon_type', 'is_active', 'created_at']
    search_fields = ['name']


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'status', 'coupon_code', 'issued_at', 'expires_at']
    list_filter = ['status', 'issued_at', 'expires_at']
    search_fields = ['user__username', 'coupon_code', 'coupon__name']
    readonly_fields = ['issued_at', 'used_at']


@admin.register(ReadingStreak)
class ReadingStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_reading_date', 'updated_at']
    list_filter = ['last_reading_date', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']