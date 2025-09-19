from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction, models
from django.conf import settings
from decimal import Decimal
import anthropic
from books.models import UserBook
from reading.models import ReadingNote
from sunflower.models import SunflowerGrowth
from .models import BookReview


@login_required
def ai_chat_main(request):
    """
    AI 채팅 메인 페이지 - 독후감을 생성할 책 선택
    """
    # 독서 노트가 있는 책들만 필터링
    books_with_notes = UserBook.objects.filter(
        user=request.user
    ).annotate(
        note_count=models.Count('readingnote')
    ).filter(
        note_count__gt=0
    ).order_by('-updated_at')

    # 진행 상황 계산
    books_data = []
    for book in books_with_notes:
        progress_percent = 0
        if book.total_pages > 0:
            progress_percent = round((book.current_page * 100) / book.total_pages, 1)

        books_data.append({
            'book': book,
            'progress_percent': progress_percent,
            'note_count': book.note_count
        })

    return render(request, 'chat/ai_chat_main.html', {
        'books_data': books_data
    })


@login_required
def generate_review(request, book_id):
    book = get_object_or_404(UserBook, id=book_id, user=request.user)
    notes = ReadingNote.objects.filter(user_book=book).order_by('page_number')

    if not notes.exists():
        messages.error(request, '독후감을 생성하려면 최소 1개 이상의 독서 노트가 필요합니다.')
        return redirect('reading:detail', book_id=book_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        liked_point = request.POST.get('liked_point', '').strip()
        disliked_point = request.POST.get('disliked_point', '').strip()

        if not rating or (not liked_point and not disliked_point):
            messages.error(request, '평점과 좋았던 점 또는 별로였던 점 중 하나는 반드시 입력해주세요.')
            return render(request, 'chat/generate_review.html', {
                'book': book,
                'notes': notes,
                'rating': rating,
                'liked_point': liked_point,
                'disliked_point': disliked_point,
            })

        try:
            review_content = generate_ai_review(book, notes, rating, liked_point, disliked_point)

            # 독후감 저장 또는 업데이트
            book_review, created = BookReview.objects.update_or_create(
                user_book=book,
                defaults={
                    'rating': int(rating),
                    'liked_point': liked_point,
                    'disliked_point': disliked_point,
                    'review_content': review_content,
                }
            )

            return redirect('chat:view_review', book_id=book.id)

        except Exception as e:
            messages.error(request, f'독후감 생성 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'chat/generate_review.html', {
                'book': book,
                'notes': notes,
                'rating': rating,
                'liked_point': liked_point,
                'disliked_point': disliked_point,
            })

    return render(request, 'chat/generate_review.html', {
        'book': book,
        'notes': notes,
    })


@login_required
def edit_review(request, book_id):
    """
    독후감 수정 페이지
    """
    book = get_object_or_404(UserBook, id=book_id, user=request.user)

    try:
        review = BookReview.objects.get(user_book=book)
    except BookReview.DoesNotExist:
        messages.error(request, '수정할 독후감이 없습니다.')
        return redirect('reading:detail', book_id=book_id)

    if request.method == 'POST':
        review_content = request.POST.get('review_content', '').strip()

        if not review_content:
            messages.error(request, '독후감 내용을 입력해주세요.')
            return render(request, 'chat/edit_review.html', {
                'book': book,
                'review': review,
            })

        # 독후감 업데이트
        review.review_content = review_content
        review.save()

        messages.success(request, '독후감이 성공적으로 수정되었습니다.')
        return redirect('chat:view_review', book_id=book.id)

    return render(request, 'chat/edit_review.html', {
        'book': book,
        'review': review,
    })


@login_required
def view_review(request, book_id):
    """
    독후감 결과 보기 (GET 요청 전용)
    """
    book = get_object_or_404(UserBook, id=book_id, user=request.user)

    try:
        review = BookReview.objects.get(user_book=book)
    except BookReview.DoesNotExist:
        messages.error(request, '독후감이 없습니다. 먼저 독후감을 생성해주세요.')
        return redirect('reading:detail', book_id=book_id)

    return render(request, 'chat/review_result.html', {
        'book': book,
        'review': review,
    })


@login_required
def delete_review(request, book_id):
    """
    독후감 삭제
    """
    if request.method == 'POST':
        book = get_object_or_404(UserBook, id=book_id, user=request.user)

        try:
            review = BookReview.objects.get(user_book=book)
            review.delete()
            messages.success(request, '독후감이 삭제되었습니다.')
        except BookReview.DoesNotExist:
            messages.error(request, '삭제할 독후감이 없습니다.')

    return redirect('reading:detail', book_id=book_id)


def generate_ai_review(book, notes, rating, liked_point, disliked_point):
    """
    Claude API를 사용하여 독후감 생성
    """
    try:
        claude_api_key = getattr(settings, 'CLAUDE_API_KEY', None)
        if not claude_api_key:
            raise Exception("Claude API 키가 설정되지 않았습니다.")

        try:
            client = anthropic.Anthropic(api_key=claude_api_key)
        except TypeError as e:
            if 'proxies' in str(e):
                # anthropic 라이브러리의 이전 버전 호환성을 위한 대안
                client = anthropic.Client(api_key=claude_api_key)
            else:
                raise e

        # 노트 내용을 텍스트로 정리
        notes_text = ""
        for note in notes:
            notes_text += f"[{note.page_number}페이지] {note.note_content}\n"

        # 평가 요소 정리
        evaluation_text = f"평점: {rating}/5점\n"
        if liked_point:
            evaluation_text += f"좋았던 점: {liked_point}\n"
        if disliked_point:
            evaluation_text += f"별로였던 점: {disliked_point}\n"

        # AI 프롬프트 구성
        prompt = f"""다음은 한 독자의 실제 독서 기록입니다. 이를 바탕으로 자연스럽고 진솔한 독후감을 1인칭 시점에서 작성해주세요.

【독서 정보】
책 제목: {book.book_title}
저자: {book.book_author}
읽은 분량: {book.current_page}페이지 / 전체 {book.total_pages}페이지

【독서 노트 내용】
{notes_text}

【독자의 평가】
{evaluation_text}

【독후감 작성 요구사항】
- 위의 독서 노트 내용을 가지고 자연스럽게 활용
- 독자의 솔직한 감상과 평가를 반영
- 메모가 이상하다면 무시하고 일반적인 독후감 작성
- 일반적인 서론/본론/결론 구조보다는 자연스러운 감상 흐름으로 작성
- 템플릿이나 형식적인 표현 지양
- 700-900자 내외의 적당한 길이
- 마무리는 간단하게, 불필요한 인사말 없이

이제 이 독자가 직접 쓴 것처럼 자연스러운 독후감을 작성해주세요:"""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return message.content[0].text

    except Exception as e:
        raise Exception(f"AI 독후감 생성 실패: {str(e)}")
