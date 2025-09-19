from django.urls import path
from . import views

app_name = 'sunflower'

urlpatterns = [
    path('', views.home, name='home'),
]