"""List recent CREATED Payment records with razorpay_order_id for local testing."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from payments.models import Payment


def main():
    qs = Payment.objects.filter(status=Payment.Status.CREATED).order_by('-created_at')[:10]
    if not qs:
        print('NO_CREATED_PAYMENTS')
        return
    for p in qs:
        print(p.id, p.razorpay_order_id, p.status, p.amount, p.user_id, p.created_at.isoformat())


if __name__ == '__main__':
    main()
