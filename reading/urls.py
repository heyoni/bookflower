from django.urls import path
from . import views

app_name = 'reading'

urlpatterns = [
    path('', views.my_books, name='my_books'),
    path('<int:book_id>/', views.detail, name='detail'),
    path('<int:book_id>/progress/', views.update_progress, name='update_progress'),
    path('<int:book_id>/update-with-note/', views.update_with_note, name='update_with_note'),
    path('<int:book_id>/notes/', views.add_note, name='add_note'),
    path('<int:book_id>/notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('<int:book_id>/delete/', views.delete_book, name='delete_book'),
]