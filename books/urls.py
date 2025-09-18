from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('search/', views.search_books, name='search'),
    path('<int:book_id>/', views.book_detail, name='detail'),
    path('add/', views.add_book_from_api, name='add_from_api'),
]