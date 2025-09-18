from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ReadingSession, Note
from books.models import Book


@login_required
def start_reading(request):
    """독서 기록 페이지"""
    recent_books = Book.objects.filter(
        readingsession__user=request.user
    ).distinct()[:5]

    context = {
        'recent_books': recent_books,
    }

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book_title = request.POST.get('book_title')
        book_author = request.POST.get('book_author', '')

        # 새 책 추가 또는 기존 책 선택
        if book_title:
            book, created = Book.objects.get_or_create(
                title=book_title,
                defaults={'author': book_author}
            )
        elif book_id:
            book = get_object_or_404(Book, id=book_id)
        else:
            messages.error(request, '책을 선택하거나 입력해주세요.')
            return render(request, 'reading/start.html', context)

        # 독서 세션 생성
        session = ReadingSession.objects.create(
            user=request.user,
            book=book
        )

        return redirect('reading:session', session_id=session.id)

    return render(request, 'reading/start.html', context)


@login_required
def reading_session(request, session_id):
    """독서 기록 페이지"""
    session = get_object_or_404(ReadingSession, id=session_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'complete_session':
            # 독서 완료 기록
            pages_read = request.POST.get('pages_read', 0)
            try:
                pages_read = int(pages_read)
            except (ValueError, TypeError):
                pages_read = 0

            session.pages_read = pages_read
            session.completed = True

            # 페이지 수에 따른 포인트 계산 (1페이지 = 1포인트)
            if pages_read > 0:
                session.earned_points = pages_read
                request.user.points += pages_read
                request.user.save()
                messages.success(request, f'독서를 완료했습니다! {pages_read}페이지 읽어서 {pages_read}P를 획득했어요 🌻')
            else:
                messages.info(request, '읽은 페이지 수를 입력해주세요.')
                return render(request, 'reading/session.html', {
                    'session': session,
                    'notes': Note.objects.filter(user=request.user, book=session.book).order_by('-created_at')
                })

            session.save()
            return redirect('reading:session_complete', session_id=session.id)

        elif action == 'add_note':
            # 노트 추가
            note_text = request.POST.get('note')
            page_until = request.POST.get('page_until')

            if note_text:
                Note.objects.create(
                    user=request.user,
                    book=session.book,
                    note=note_text,
                    page_until=int(page_until) if page_until else None
                )
                messages.success(request, '노트가 추가되었습니다!')

    # 현재 세션의 노트들
    notes = Note.objects.filter(
        user=request.user,
        book=session.book
    ).order_by('-created_at')

    context = {
        'session': session,
        'notes': notes,
    }

    return render(request, 'reading/session.html', context)


@login_required
def session_complete(request, session_id):
    """독서 세션 완료 페이지"""
    session = get_object_or_404(ReadingSession, id=session_id, user=request.user)

    context = {
        'session': session,
    }
    return render(request, 'reading/complete.html', context)


@login_required
def my_notes(request):
    """내 노트 목록"""
    notes = Note.objects.filter(user=request.user).select_related('book').order_by('-created_at')

    context = {
        'notes': notes,
    }
    return render(request, 'reading/notes.html', context)
