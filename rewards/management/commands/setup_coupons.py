from django.core.management.base import BaseCommand
from rewards.models import CafeCoupon


class Command(BaseCommand):
    help = '기본 카페 쿠폰 데이터 생성'

    def handle(self, *args, **options):
        coupons_data = [
            {
                'name': '아메리카노 쿠폰',
                'coupon_type': 'americano',
                'required_points': 500,
                'description': '지역 카페에서 사용 가능한 아메리카노 쿠폰입니다. 30일간 유효합니다.'
            },
            {
                'name': '카페라떼 쿠폰',
                'coupon_type': 'latte',
                'required_points': 800,
                'description': '지역 카페에서 사용 가능한 카페라떼 쿠폰입니다. 30일간 유효합니다.'
            },
            {
                'name': '디저트 쿠폰',
                'coupon_type': 'dessert',
                'required_points': 1000,
                'description': '지역 카페에서 사용 가능한 디저트 쿠폰입니다. 케이크, 쿠키 등을 즐기세요. 30일간 유효합니다.'
            },
        ]

        for coupon_data in coupons_data:
            coupon, created = CafeCoupon.objects.get_or_create(
                name=coupon_data['name'],
                defaults=coupon_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'쿠폰 생성: {coupon.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'이미 존재하는 쿠폰: {coupon.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('카페 쿠폰 설정이 완료되었습니다.')
        )