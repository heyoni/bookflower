from django.urls import path
from . import views

app_name = 'reading'

urlpatterns = [
    path('start/', views.start_reading, name='start'),
    path('session/<int:session_id>/', views.reading_session, name='session'),
    path('complete/<int:session_id>/', views.session_complete, name='session_complete'),
    path('notes/', views.my_notes, name='notes'),
]