from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('points', 'badges')}),
    )
    list_display = ('username', 'email', 'points', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'points')
    search_fields = ('username', 'email')
