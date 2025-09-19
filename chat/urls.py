from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ai_chat_main, name='main'),
    path('<int:book_id>/generate/', views.generate_review, name='generate_review'),
    path('<int:book_id>/view/', views.view_review, name='view_review'),
    path('<int:book_id>/edit/', views.edit_review, name='edit_review'),
    path('<int:book_id>/delete/', views.delete_review, name='delete_review'),
]