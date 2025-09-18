from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from reading.models import ReadingSession, Note
from reviews.models import Review


def dashboard(request):
    """메인 대시보드 뷰"""
    context = {
        'reading_sessions_count': 0,
        'notes_count': 0,
        'reviews_count': 0,
        'recent_sessions': [],
    }

    if request.user.is_authenticated:
        # 사용자 통계
        context['reading_sessions_count'] = ReadingSession.objects.filter(
            user=request.user
        ).count()

        context['notes_count'] = Note.objects.filter(
            user=request.user
        ).count()

        context['reviews_count'] = Review.objects.filter(
            user=request.user
        ).count()

        # 최근 독서 세션
        context['recent_sessions'] = ReadingSession.objects.filter(
            user=request.user
        ).select_related('book').order_by('-created_at')[:5]

    return render(request, 'dashboard.html', context)