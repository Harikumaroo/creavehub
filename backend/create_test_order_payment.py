"""Create a minimal Order and Payment record for local Razorpay testing.

Usage: python backend/create_test_order_payment.py
Outputs the created razorpay_order_id which can be used with the simulate script.
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, RestaurantAddress
from orders.models import Order
from payments.models import Payment
from django.utils import timezone
import uuid


def main():
    User = get_user_model()
    user = User.objects.filter(mobile_number='+919999999999').first() or User.objects.first()
    if not user:
        print('No user available in DB. Create a user first.')
        return

    rest = Restaurant.objects.filter(is_active=True).first()
    if not rest:
        rest = Restaurant.objects.create(
            name='Test Restaurant',
            description='Auto-created test restaurant',
            rating=4.5,
            average_delivery_time=30,
            minimum_order_amount=Decimal('50.00'),
            is_pure_veg=False,
            is_active=True,
            delivery_fee=Decimal('30.00'),
            is_open=True,
        )
        RestaurantAddress.objects.create(
            restaurant=rest,
            address='123 Test Lane',
            city='TestCity',
            state='TestState',
            pincode='560001',
        )

    subtotal = Decimal('100.00')
    delivery_fee = rest.delivery_fee or Decimal('30.00')
    tax = (subtotal * Decimal('0.05')).quantize(Decimal('0.01'))
    grand_total = subtotal + delivery_fee + tax

    order = Order.objects.create(
        user=user,
        restaurant=rest,
        status=Order.Status.PENDING,
        payment_status=Order.PaymentStatus.PENDING,
        payment_method=Order.PaymentMethod.RAZORPAY,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax=tax,
        grand_total=grand_total,
        delivery_address='Test Address',
        delivery_city='TestCity',
        delivery_pincode='560001',
        estimated_delivery_time=rest.average_delivery_time,
        instructions='Test order',
    )

    rz_order_id = f'test_rz_{uuid.uuid4().hex[:12]}'
    payment = Payment.objects.create(
        user=user,
        order=order,
        razorpay_order_id=rz_order_id,
        amount=grand_total,
        currency='INR',
        status=Payment.Status.CREATED,
        gateway_response={},
    )

    order.razorpay_order_id = rz_order_id
    order.save(update_fields=['razorpay_order_id'])

    print('CREATED', rz_order_id)


if __name__ == '__main__':
    main()
