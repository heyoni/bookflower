from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    # 웹 페이지
    path('', views.points_dashboard, name='dashboard'),
    path('history/', views.point_history, name='point_history'),
    path('coupons/', views.my_coupons, name='my_coupons'),
    path('exchange/<int:coupon_id>/', views.exchange_coupon, name='exchange_coupon'),
    path('use/<str:coupon_code>/', views.use_coupon_page, name='use_coupon'),

    # API 엔드포인트
    path('api/points/', views.api_user_points, name='api_user_points'),
    path('api/coupons/available/', views.api_available_coupons, name='api_available_coupons'),
    path('api/coupons/my/', views.api_my_coupons, name='api_my_coupons'),
]