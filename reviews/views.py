from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Review
from books.models import Book
from reading.models import Note
import json


@login_required
def create_review(request, book_id):
    """AI 독후감 생성 페이지"""
    book = get_object_or_404(Book, id=book_id)

    # 이미 리뷰가 있는지 확인
    existing_review = Review.objects.filter(user=request.user, book=book).first()
    if existing_review:
        return redirect('reviews:detail', review_id=existing_review.id)

    # 사용자의 노트들 가져오기
    notes = Note.objects.filter(user=request.user, book=book).order_by('created_at')

    context = {
        'book': book,
        'notes': notes,
        'notes_count': notes.count(),
    }

    if request.method == 'POST':
        # AI 독후감 생성 (실제로는 OpenAI API 등을 사용)
        ai_content = generate_ai_review(book, notes)

        review = Review.objects.create(
            user=request.user,
            book=book,
            content=ai_content,
            generated_by_ai=True
        )

        messages.success(request, 'AI 독후감이 생성되었습니다!')
        return redirect('reviews:detail', review_id=review.id)

    return render(request, 'reviews/create.html', context)


@login_required
def review_detail(request, review_id):
    """독후감 상세 페이지"""
    review = get_object_or_404(Review, id=review_id, user=request.user)

    context = {
        'review': review,
    }
    return render(request, 'reviews/detail.html', context)


@login_required
def my_reviews(request):
    """내 독후감 목록"""
    reviews = Review.objects.filter(user=request.user).select_related('book').order_by('-created_at')

    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/list.html', context)


def generate_ai_review(book, notes):
    """AI 독후감 생성 (모의 구현)"""
    # 실제로는 OpenAI API나 다른 AI 서비스를 사용
    # 여기서는 템플릿 기반으로 간단하게 구현

    notes_text = ""
    if notes.exists():
        notes_text = "\n".join([f"- {note.note}" for note in notes[:5]])

    ai_content = f"""『{book.title}』을 읽고

이 책을 읽으며 많은 생각을 하게 되었습니다. {book.author if book.author else '저자'}의 섬세한 문체와 깊이 있는 내용이 인상적이었습니다.

📖 **주요 인사이트**
{notes_text if notes_text else "이 책을 통해 새로운 관점을 얻을 수 있었습니다."}

🌟 **느낀 점**
독서를 통해 얻은 깨달음이 일상생활에도 많은 도움이 될 것 같습니다. 특히 책에서 제시하는 관점들이 현재의 나에게 필요한 메시지였다고 생각합니다.

💭 **추천 이유**
이 책은 비슷한 고민을 하고 있는 사람들에게 좋은 길잡이가 될 것이라고 생각합니다. 읽는 내내 공감할 수 있는 부분이 많았고, 마지막 페이지를 덮을 때까지 몰입할 수 있었습니다.

책바라기 AI가 작성한 독후감입니다 🤖"""

    return ai_content
