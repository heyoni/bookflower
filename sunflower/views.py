from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
from .models import SunflowerGrowth
from books.models import UserBook


@login_required
def home(request):
    sunflower, created = SunflowerGrowth.objects.get_or_create(
        user=request.user,
        defaults={
            'total_pages_read': 0,
            'current_height_cm': 0,
            'level': 1
        }
    )

    # 실제 읽은 총 페이지 수 계산
    user_books = UserBook.objects.filter(user=request.user)
    total_pages = sum(book.current_page for book in user_books)

    # 해바라기 성장 업데이트
    if sunflower.total_pages_read != total_pages:
        sunflower.total_pages_read = total_pages
        # 키 계산: 100페이지당 1cm 성장 (1페이지당 0.01cm)
        sunflower.current_height_cm = Decimal(str(total_pages * 0.01))
        # 레벨 계산: 100페이지마다 레벨업
        sunflower.level = max(1, int(total_pages / 100) + 1)
        sunflower.save()

    recent_books_queryset = UserBook.objects.filter(
        user=request.user,
        status__in=['reading', 'completed']
    ).order_by('-updated_at')[:3]

    recent_books = []
    for book in recent_books_queryset:
        progress_percent = 0
        if book.total_pages > 0:
            progress_percent = round((book.current_page * 100) / book.total_pages, 1)

        recent_books.append({
            'book': book,
            'progress_percent': progress_percent
        })

    reading_books = UserBook.objects.filter(
        user=request.user,
        status='reading'
    ).count()

    completed_books = UserBook.objects.filter(
        user=request.user,
        status='completed'
    ).count()

    context = {
        'sunflower': sunflower,
        'recent_books': recent_books,
        'reading_books': reading_books,
        'completed_books': completed_books,
    }

    return render(request, 'sunflower/home.html', context)
