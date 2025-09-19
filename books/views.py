from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import UserBook
import requests
import json
import xml.etree.ElementTree as ET


@login_required
def search(request):
    query = request.GET.get('q', '')
    books = []

    if query:
        books = search_books_api(query)

    return render(request, 'books/search.html', {
        'query': query,
        'books': books
    })


@login_required
def add_book(request):
    if request.method == 'POST':
        external_book_id = request.POST.get('external_book_id')
        book_title = request.POST.get('book_title')
        book_author = request.POST.get('book_author', '')
        total_pages = request.POST.get('total_pages', 0)

        # ItemLookUp API를 사용해서 상세 정보 가져오기 (페이지 수 포함)
        if external_book_id:
            detailed_info = get_book_details(external_book_id)
            if detailed_info and detailed_info.get('page_count', 0) > 0:
                total_pages = detailed_info['page_count']
            else:
                # API에서 페이지 수를 가져오지 못한 경우 기본값 사용
                try:
                    total_pages = int(total_pages) if total_pages else 0
                except ValueError:
                    total_pages = 0
        else:
            try:
                total_pages = int(total_pages) if total_pages else 0
            except ValueError:
                total_pages = 0

        if external_book_id and book_title:
            book, created = UserBook.objects.get_or_create(
                user=request.user,
                external_book_id=external_book_id,
                defaults={
                    'book_title': book_title,
                    'book_author': book_author,
                    'total_pages': total_pages,
                    'status': 'reading',
                    'current_page': 0
                }
            )

            if created:
                page_info = f" ({total_pages}페이지)" if total_pages > 0 else ""
                messages.success(request, f'"{book_title}"{page_info} 책이 내 책장에 추가되었습니다!')
            else:
                messages.info(request, '이미 내 책장에 있는 책입니다.')

            return redirect('reading:detail', book_id=book.id)
        else:
            messages.error(request, '책 정보가 올바르지 않습니다.')

    return redirect('books:search')


def search_books_api(query, page_no=1):
    """
    알라딘 API를 사용한 도서 검색
    """
    if not query:
        return []

    try:
        # API 키 확인
        ttb_key = getattr(settings, 'ALADIN_TTB_KEY', None)
        if not ttb_key:
            return get_fallback_books(query)

        # API URL 구성
        api_url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
        params = {
            'ttbkey': ttb_key,
            'Query': query,
            'QueryType': 'Keyword',
            'MaxResults': 10,
            'start': page_no,
            'SearchTarget': 'Book',
            'output': 'xml',
            'Version': '20131101'
        }

        # API 호출
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        # XML 파싱
        root = ET.fromstring(response.content)

        # 네임스페이스 정의
        namespace = {'ns': 'http://www.aladin.co.kr/ttb/apiguide.aspx'}

        # 네임스페이스를 사용해서 item 찾기
        items = root.findall('.//ns:item', namespace)

        # 네임스페이스 없이도 시도
        if len(items) == 0:
            items = root.findall('.//item')

        books = []
        # 알라딘 API 응답 구조: item들
        for item in items:
            try:
                # 필수 정보 추출 (네임스페이스 사용)
                title = item.find('ns:title', namespace)
                author = item.find('ns:author', namespace)
                publisher = item.find('ns:publisher', namespace)
                pub_date = item.find('ns:pubDate', namespace)
                isbn = item.find('ns:isbn13', namespace)
                isbn10 = item.find('ns:isbn', namespace)

                # 알라딘에서 제공하는 추가 정보
                description = item.find('ns:description', namespace)
                cover = item.find('ns:cover', namespace)
                price = item.find('ns:priceStandard', namespace)
                category = item.find('ns:categoryName', namespace)

                # 검색 API에서는 페이지 수 정보가 제공되지 않음
                # 실제 페이지 수는 ItemLookUp API에서 가져옴
                page_count = 0

                # 저자 정보 처리
                author_text = author.text if author is not None and author.text else '저자 미상'
                author_list = []
                if author_text and author_text != '저자 미상':
                    # 여러 저자는 쉼표로 구분됨
                    author_list = [a.strip() for a in author_text.split(',') if a.strip()]

                if not author_list:
                    author_list = ['저자 미상']

                # 설명 텍스트 구성
                description_text = description.text if description is not None and description.text else ''
                if category is not None and category.text:
                    description_text = f"📚 {category.text}" + (f" | {description_text}" if description_text else "")

                # ISBN 처리 (13자리 우선, 없으면 10자리)
                book_isbn = ''
                if isbn is not None and isbn.text:
                    book_isbn = isbn.text
                elif isbn10 is not None and isbn10.text:
                    book_isbn = isbn10.text

                book_data = {
                    'id': book_isbn if book_isbn else f'aladin_{hash(title.text if title is not None else "no_title")}',
                    'title': title.text if title is not None else '제목 없음',
                    'authors': author_list,
                    'description': description_text if description_text else '상세 정보가 없습니다.',
                    'page_count': page_count,
                    'thumbnail': cover.text if cover is not None and cover.text else None,
                    'published_date': pub_date.text if pub_date is not None else '',
                    'publisher': publisher.text if publisher is not None else '',
                    'isbn': book_isbn,
                    'price': price.text if price is not None and price.text else ''
                }

                books.append(book_data)

            except Exception as e:
                # 개별 책 파싱 오류는 로그만 남기고 계속 진행
                continue

        return books

    except requests.RequestException as e:
        return get_fallback_books(query)

    except ET.ParseError as e:
        return get_fallback_books(query)

    except Exception as e:
        return get_fallback_books(query)


def get_book_details(isbn):
    """
    알라딘 ItemLookUp API를 사용해서 개별 도서의 상세 정보 가져오기
    페이지 수 정보를 포함
    """
    try:
        ttb_key = getattr(settings, 'ALADIN_TTB_KEY', None)
        if not ttb_key:
            return None

        # ItemLookUp API URL 구성
        api_url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
        params = {
            'ttbkey': ttb_key,
            'itemIdType': 'ISBN13',
            'ItemId': isbn,
            'output': 'xml',
            'Version': '20131101',
            'OptResult': 'ebookList,usedList,reviewList'
        }

        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        # XML 파싱
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.aladin.co.kr/ttb/apiguide.aspx'}

        # item 찾기
        item = root.find('.//ns:item', namespace)
        if item is None:
            return None

        # 페이지 수 정보 추출 (subInfo > itemPage에서)
        sub_info = item.find('ns:subInfo', namespace)
        page_count = 0

        if sub_info is not None:
            # itemPage 요소 찾기
            item_page = sub_info.find('ns:itemPage', namespace)
            if item_page is not None and item_page.text:
                try:
                    page_count = int(item_page.text.strip())
                except ValueError:
                    page_count = 0

        return {
            'page_count': page_count
        }

    except Exception as e:
        return None


def get_fallback_books(query):
    """
    API 오류 시 사용할 더미 데이터
    """
    return [
        {
            'id': f'fallback_{query}_1',
            'title': f'🚨 API 연결 오류 - {query} 관련 샘플 도서',
            'authors': ['샘플 저자'],
            'description': f'⚠️ 도서관 검색 API 연결에 문제가 있습니다. API 키를 확인하거나 네트워크 상태를 점검해주세요.',
            'page_count': 250,
            'thumbnail': None,
            'published_date': '2024',
            'publisher': 'API 오류',
            'isbn': ''
        }
    ] if query else []
