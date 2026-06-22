"""Simulate a successful Razorpay payment locally (test mode).

Usage:
1. Ensure you have an order with an associated Payment record created (via the API or `PaymentService.initiate_payment`).
2. Set environment variables or ensure `.env` has `RAZORPAY_KEY_SECRET`.
3. Run: `python backend/payments/simulate_razorpay_success.py <razorpay_order_id>`

This script will craft a fake `razorpay_payment_id`, compute the expected HMAC signature
using your `RAZORPAY_KEY_SECRET` and call `PaymentService.verify_payment()` to mark the
payment as PAID. Use only in local/test environments.
"""

import os
import sys
import uuid
import hashlib
import hmac

# ensure project root is on sys.path so `cravehub` settings can be imported
# ensure backend dir (where `cravehub` package lives) is on sys.path
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
import django
django.setup()

from django.conf import settings
from payments.services import PaymentService
from payments.models import Payment


def usage():
    print("Usage: python backend/payments/simulate_razorpay_success.py <razorpay_order_id>")


def main():
    if len(sys.argv) < 2:
        usage()
        return
    rz_order_id = sys.argv[1]
    try:
        payment = Payment.objects.get(razorpay_order_id=rz_order_id)
    except Payment.DoesNotExist:
        print("Payment with given razorpay_order_id not found. Run initiate first.")
        return

    if payment.status == Payment.Status.PAID:
        print("Payment already marked as PAID")
        return

    # craft fake payment id and compute signature
    fake_payment_id = f"pay_{uuid.uuid4().hex[:24]}"
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
    if not key_secret:
        print("RAZORPAY_KEY_SECRET is not configured in environment/.env")
        return

    message = f"{rz_order_id}|{fake_payment_id}".encode()
    generated_signature = hmac.new(key_secret.encode(), message, hashlib.sha256).hexdigest()

    # call verify API (acts like the webhook/SDK verification)
    try:
        payment = PaymentService.verify_payment(
            user=payment.user,
            razorpay_order_id=rz_order_id,
            razorpay_payment_id=fake_payment_id,
            razorpay_signature=generated_signature,
        )
        print(f"Simulated payment verified: payment id {payment.id}")
    except Exception as exc:
        print("Simulation failed:", exc)


if __name__ == '__main__':
    main()
