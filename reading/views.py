from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction, models
from decimal import Decimal
from books.models import UserBook
from sunflower.models import SunflowerGrowth
from .models import ReadingNote


@login_required
def my_books(request):
    books_queryset = UserBook.objects.filter(user=request.user).order_by('-updated_at')

    books = []
    for book in books_queryset:
        progress_percent = 0
        if book.total_pages > 0:
            progress_percent = round((book.current_page * 100) / book.total_pages, 1)

        books.append({
            'book': book,
            'progress_percent': progress_percent
        })

    return render(request, 'reading/my_books.html', {'books': books})


@login_required
def detail(request, book_id):
    book = get_object_or_404(UserBook, id=book_id, user=request.user)
    notes = ReadingNote.objects.filter(user_book=book).order_by('page_number')

    progress_percent = 0
    if book.total_pages > 0:
        progress_percent = round((book.current_page * 100) / book.total_pages, 1)

    # 독후감이 있는지 확인 (chat 앱에서 확인)
    try:
        from chat.models import BookReview
        book_review = BookReview.objects.get(user_book=book)
        has_review = True
    except BookReview.DoesNotExist:
        book_review = None
        has_review = False

    return render(request, 'reading/detail.html', {
        'book': book,
        'notes': notes,
        'progress_percent': progress_percent,
        'has_review': has_review,
        'book_review': book_review,
    })


@login_required
def update_progress(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(UserBook, id=book_id, user=request.user)

        try:
            new_page = int(request.POST.get('current_page', 0))
            new_status = request.POST.get('status', 'reading')

            if new_page < 0:
                new_page = 0
            elif new_page >= book.total_pages:
                new_page = book.total_pages
                new_status = 'completed'

            old_page = book.current_page
            pages_read = max(0, new_page - old_page)

            with transaction.atomic():
                book.current_page = new_page
                book.status = new_status
                book.save()

                # 해바라기 성장 업데이트 (페이지 변경 시에만)
                if pages_read != 0:  # 페이지가 변경된 경우 (증가 또는 감소)
                    sunflower, created = SunflowerGrowth.objects.get_or_create(
                        user=request.user,
                        defaults={
                            'total_pages_read': 0,
                            'current_height_cm': 0,
                            'level': 1
                        }
                    )

                    # 실제 읽은 총 페이지 수 재계산
                    user_books = UserBook.objects.filter(user=request.user)
                    total_pages = sum(book_item.current_page for book_item in user_books)

                    sunflower.total_pages_read = total_pages
                    sunflower.current_height_cm = Decimal(str(total_pages * 0.01))
                    sunflower.level = max(1, int(total_pages / 100) + 1)
                    sunflower.save()

            if new_status == 'completed':
                messages.success(request, f'🎉 축하합니다! "{book.book_title}"을 완독하셨습니다!')
            else:
                messages.success(request, f'독서 진행상황이 업데이트되었습니다. ({new_page}/{book.total_pages})')

        except ValueError:
            messages.error(request, '올바른 페이지 번호를 입력해주세요.')

    return redirect('reading:detail', book_id=book_id)


@login_required
def update_with_note(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(UserBook, id=book_id, user=request.user)

        try:
            new_page = int(request.POST.get('current_page', 0))
            note_page = int(request.POST.get('note_page', 0))
            note_content = request.POST.get('note_content', '')

            if new_page < 0:
                new_page = 0
            elif new_page >= book.total_pages:
                new_page = book.total_pages

            # 메모가 있는 경우에만 유효성 검사
            has_note = note_content and note_content.strip()
            if has_note:
                if note_page < 1 or note_page > book.total_pages:
                    messages.error(request, f'노트 페이지는 1-{book.total_pages} 사이여야 합니다.')
                    return redirect('reading:detail', book_id=book_id)

            old_page = book.current_page
            pages_read = new_page - old_page

            with transaction.atomic():
                # 진행상황 업데이트
                book.current_page = new_page
                if new_page >= book.total_pages:
                    book.status = 'completed'
                book.save()

                # 노트 추가 (메모가 있는 경우에만)
                if has_note:
                    ReadingNote.objects.create(
                        user_book=book,
                        page_number=note_page,
                        note_content=note_content
                    )

                # 해바라기 성장 업데이트
                if pages_read != 0:
                    sunflower, created = SunflowerGrowth.objects.get_or_create(
                        user=request.user,
                        defaults={
                            'total_pages_read': 0,
                            'current_height_cm': 0,
                            'level': 1
                        }
                    )

                    user_books = UserBook.objects.filter(user=request.user)
                    total_pages = sum(book_item.current_page for book_item in user_books)

                    sunflower.total_pages_read = total_pages
                    sunflower.current_height_cm = Decimal(str(total_pages * 0.01))
                    sunflower.level = max(1, int(total_pages / 100) + 1)
                    sunflower.save()

            if book.status == 'completed':
                if has_note:
                    messages.success(request, f'🎉 축하합니다! "{book.book_title}"을 완독하셨습니다! 메모도 저장되었어요.')
                else:
                    messages.success(request, f'🎉 축하합니다! "{book.book_title}"을 완독하셨습니다!')
            else:
                if has_note:
                    messages.success(request, f'독서 진행상황과 {note_page}페이지 메모가 저장되었습니다.')
                else:
                    messages.success(request, f'독서 진행상황이 업데이트되었습니다. ({new_page}/{book.total_pages})')

        except ValueError:
            messages.error(request, '올바른 페이지 번호를 입력해주세요.')

    return redirect('reading:detail', book_id=book_id)


@login_required
def add_note(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(UserBook, id=book_id, user=request.user)

        page_number = request.POST.get('page_number')
        note_content = request.POST.get('note_content')

        if page_number and note_content:
            try:
                page_number = int(page_number)
                if 1 <= page_number <= book.total_pages:
                    ReadingNote.objects.create(
                        user_book=book,
                        page_number=page_number,
                        note_content=note_content
                    )
                    messages.success(request, f'{page_number}페이지 노트가 추가되었습니다.')
                else:
                    messages.error(request, f'페이지 번호는 1-{book.total_pages} 사이여야 합니다.')
            except ValueError:
                messages.error(request, '올바른 페이지 번호를 입력해주세요.')
        else:
            messages.error(request, '페이지 번호와 노트 내용을 모두 입력해주세요.')

    return redirect('reading:detail', book_id=book_id)


@login_required
def delete_note(request, book_id, note_id):
    if request.method == 'POST':
        book = get_object_or_404(UserBook, id=book_id, user=request.user)
        note = get_object_or_404(ReadingNote, id=note_id, user_book=book)

        page_number = note.page_number
        note.delete()

        messages.success(request, f'{page_number}페이지 노트가 삭제되었습니다.')

    return redirect('reading:detail', book_id=book_id)


@login_required
def delete_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(UserBook, id=book_id, user=request.user)
        book_title = book.book_title

        with transaction.atomic():
            # 관련된 모든 노트도 함께 삭제됨 (CASCADE)
            book.delete()

            # 해바라기 성장 업데이트 (책 삭제 후 총 페이지 수 재계산)
            try:
                sunflower = SunflowerGrowth.objects.get(user=request.user)
                user_books = UserBook.objects.filter(user=request.user)
                total_pages = sum(book_item.current_page for book_item in user_books)

                sunflower.total_pages_read = total_pages
                sunflower.current_height_cm = Decimal(str(total_pages * 0.01))
                sunflower.level = max(1, int(total_pages / 100) + 1)
                sunflower.save()
            except SunflowerGrowth.DoesNotExist:
                # 해바라기가 없는 경우는 무시
                pass

        messages.success(request, f'"{book_title}" 책이 내 책장에서 삭제되었습니다.')

    return redirect('reading:my_books')


