from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Book


def search_books(request):
    """책 검색 페이지"""
    books = []
    query = request.GET.get('q', '')
    api_results = []

    if query:
        # 로컬 데이터베이스 검색
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )[:10]

        # 임시로 샘플 책들을 보여줌 (실제로는 Google Books API 등을 사용)
        if not books.exists():  # 로컬에 검색 결과가 없을 때만
            sample_books = [
                {'title': f'{query} 관련 도서 1', 'author': '저자 1', 'description': '이 책은 검색하신 주제와 관련된 내용을 다루고 있습니다.'},
                {'title': f'{query} 관련 도서 2', 'author': '저자 2', 'description': '해당 주제에 대한 심도 있는 분석을 제공합니다.'},
                {'title': f'{query} 관련 도서 3', 'author': '저자 3', 'description': '실용적인 접근 방식으로 설명한 도서입니다.'},
            ]
            api_results = sample_books

    context = {
        'query': query,
        'books': books,
        'api_results': api_results,
    }
    return render(request, 'books/search.html', context)


def book_detail(request, book_id):
    """책 상세 페이지"""
    book = get_object_or_404(Book, id=book_id)

    context = {
        'book': book,
    }

    if request.user.is_authenticated:
        # 사용자의 독서 기록
        from reading.models import ReadingSession, Note
        from reviews.models import Review

        context['reading_sessions'] = ReadingSession.objects.filter(
            user=request.user, book=book
        ).order_by('-start_time')

        context['notes'] = Note.objects.filter(
            user=request.user, book=book
        ).order_by('-created_at')

        context['review'] = Review.objects.filter(
            user=request.user, book=book
        ).first()

    return render(request, 'books/detail.html', context)


@login_required
def add_book_from_api(request):
    """API에서 책을 로컬 DB에 추가"""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')

        if title and author:
            book, created = Book.objects.get_or_create(
                title=title,
                defaults={'author': author}
            )
            return JsonResponse({
                'success': True,
                'book_id': book.id,
                'created': created
            })

    return JsonResponse({'success': False})
