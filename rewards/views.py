from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from .models import UserPoint, PointHistory, CafeCoupon, UserCoupon, ReadingStreak
from .services import CouponService


@login_required
def points_dashboard(request):
    """포인트 대시보드"""
    user_points, created = UserPoint.objects.get_or_create(user=request.user)
    reading_streak, created = ReadingStreak.objects.get_or_create(user=request.user)

    # 최근 포인트 내역
    point_history = PointHistory.objects.filter(user=request.user)[:10]

    # 사용 가능한 쿠폰들
    available_coupons = CafeCoupon.objects.filter(is_active=True)

    # 내 쿠폰함
    my_coupons = UserCoupon.objects.filter(
        user=request.user,
        status='available'
    ).order_by('-issued_at')

    context = {
        'user_points': user_points,
        'reading_streak': reading_streak,
        'point_history': point_history,
        'available_coupons': available_coupons,
        'my_coupons': my_coupons,
    }
    return render(request, 'rewards/dashboard.html', context)


@login_required
def point_history(request):
    """포인트 내역 페이지"""
    history_list = PointHistory.objects.filter(user=request.user)
    paginator = Paginator(history_list, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'rewards/point_history.html', context)


@login_required
@require_POST
def exchange_coupon(request, coupon_id):
    """포인트로 쿠폰 교환"""
    coupon = get_object_or_404(CafeCoupon, id=coupon_id, is_active=True)

    user_coupon = CouponService.exchange_points_for_coupon(request.user, coupon_id)

    if user_coupon:
        return JsonResponse({
            'success': True,
            'message': f'{coupon.name}을(를) 성공적으로 교환했습니다!',
            'coupon_code': user_coupon.coupon_code
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '포인트가 부족하거나 쿠폰 교환에 실패했습니다.'
        })


@login_required
def my_coupons(request):
    """내 쿠폰함"""
    coupons_list = UserCoupon.objects.filter(user=request.user).order_by('-issued_at')
    paginator = Paginator(coupons_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'rewards/my_coupons.html', context)


def use_coupon_page(request, coupon_code):
    """쿠폰 사용 페이지 (카페 직원용)"""
    if request.method == 'POST':
        success, message = CouponService.use_coupon(coupon_code)
        return JsonResponse({
            'success': success,
            'message': message
        })

    try:
        user_coupon = UserCoupon.objects.get(coupon_code=coupon_code)
        context = {
            'user_coupon': user_coupon,
        }
        return render(request, 'rewards/use_coupon.html', context)
    except UserCoupon.DoesNotExist:
        context = {
            'error': '유효하지 않은 쿠폰 코드입니다.'
        }
        return render(request, 'rewards/use_coupon.html', context)


# API 엔드포인트들
@login_required
def api_user_points(request):
    """사용자 포인트 정보 API"""
    user_points, created = UserPoint.objects.get_or_create(user=request.user)
    reading_streak, created = ReadingStreak.objects.get_or_create(user=request.user)

    return JsonResponse({
        'total_points': user_points.total_points,
        'available_points': user_points.available_points,
        'used_points': user_points.used_points,
        'current_streak': reading_streak.current_streak,
        'longest_streak': reading_streak.longest_streak,
    })


@login_required
def api_available_coupons(request):
    """사용 가능한 쿠폰 목록 API"""
    coupons = CafeCoupon.objects.filter(is_active=True)
    coupons_data = []

    for coupon in coupons:
        coupons_data.append({
            'id': coupon.id,
            'name': coupon.name,
            'coupon_type': coupon.coupon_type,
            'required_points': coupon.required_points,
            'description': coupon.description,
        })

    return JsonResponse({'coupons': coupons_data})


@login_required
def api_my_coupons(request):
    """내 쿠폰 목록 API"""
    coupons = UserCoupon.objects.filter(user=request.user).order_by('-issued_at')
    coupons_data = []

    for coupon in coupons:
        coupons_data.append({
            'id': coupon.id,
            'coupon_name': coupon.coupon.name,
            'coupon_type': coupon.coupon.coupon_type,
            'coupon_code': coupon.coupon_code,
            'status': coupon.status,
            'issued_at': coupon.issued_at.isoformat(),
            'expires_at': coupon.expires_at.isoformat(),
            'used_at': coupon.used_at.isoformat() if coupon.used_at else None,
        })

    return JsonResponse({'coupons': coupons_data})