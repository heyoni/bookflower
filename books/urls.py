from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('add/', views.add_book, name='add'),
]