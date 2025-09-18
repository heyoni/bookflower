from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:book_id>/', views.create_review, name='create'),
    path('<int:review_id>/', views.review_detail, name='detail'),
    path('', views.my_reviews, name='list'),
]