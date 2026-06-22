"""
CraveHub — Payments Service Layer (Phase 3)
Razorpay integration with signature verification.
"""

from __future__ import annotations
import hashlib
import hmac
import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from core.exceptions import BadRequestError, NotFoundError, ServiceUnavailableError
from orders.models import Order
from orders.services import OrderService
from .models import Payment

logger = logging.getLogger(__name__)


def _get_razorpay_client():
    """Lazy import so project works even if razorpay isn't installed yet."""
    try:
        import razorpay
        key_id     = getattr(settings, "RAZORPAY_KEY_ID", "")
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not key_id or not key_secret:
            raise ServiceUnavailableError(
                "Razorpay credentials not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
            )
        return razorpay.Client(auth=(key_id, key_secret))
    except ImportError:
        raise ServiceUnavailableError(
            "Razorpay SDK not installed. Run: pip install razorpay"
        )


class PaymentService:

    @staticmethod
    @transaction.atomic
    def initiate_payment(user, order_id: str) -> dict:
        """
        Create a Razorpay order for the given CraveHub order.
        Returns the Razorpay order details needed by the frontend SDK.
        """
        try:
            order = Order.objects.get(pk=order_id, user=user)
        except Order.DoesNotExist:
            raise NotFoundError("Order not found.")

        if order.payment_status == Order.PaymentStatus.PAID:
            raise BadRequestError("This order is already paid.")

        if order.payment_method == Order.PaymentMethod.COD:
            raise BadRequestError("COD orders do not require online payment.")

        # Amount in paise (Razorpay uses smallest currency unit)
        amount_paise = int(order.grand_total * 100)

        client = _get_razorpay_client()
        rz_order = client.order.create({
            "amount":   amount_paise,
            "currency": "INR",
            "receipt":  str(order.id)[:40],
            "notes": {
                "cravehub_order_id": str(order.id),
                "user_id":           str(user.id),
            },
        })

        # Save/update payment record
        Payment.objects.update_or_create(
            order=order,
            defaults={
                "user":               user,
                "razorpay_order_id":  rz_order["id"],
                "amount":             order.grand_total,
                "currency":           "INR",
                "status":             Payment.Status.CREATED,
                "gateway_response":   rz_order,
            },
        )

        # Store razorpay_order_id on the Order for quick lookup
        order.razorpay_order_id = rz_order["id"]
        order.save(update_fields=["razorpay_order_id"])

        return {
            "razorpay_order_id": rz_order["id"],
            "amount":            amount_paise,
            "currency":          "INR",
            "key_id":            getattr(settings, "RAZORPAY_KEY_ID", ""),
        }

    @staticmethod
    @transaction.atomic
    def verify_payment(
        user,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Payment:
        """
        Verify Razorpay signature. Mark order as PAID on success.
        """
        try:
            payment = Payment.objects.select_related("order").get(
                razorpay_order_id=razorpay_order_id,
                user=user,
            )
        except Payment.DoesNotExist:
            raise NotFoundError("Payment record not found.")

        # Signature verification
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not key_secret:
            raise BadRequestError("Razorpay secret not configured.")

        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            key_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(generated_signature, razorpay_signature):
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])
            raise BadRequestError("Payment signature verification failed.")

        # Idempotent: already PAID with same data
        if payment.status == Payment.Status.PAID:
            if (
                payment.razorpay_payment_id == razorpay_payment_id
                and payment.razorpay_signature == razorpay_signature
            ):
                return payment
            logger.warning(
                "Payment for razorpay_order_id=%s already PAID with different payment id",
                razorpay_order_id,
            )
            return payment

        # Mark payment as PAID
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature  = razorpay_signature
        payment.status              = Payment.Status.PAID
        payment.save(update_fields=[
            "razorpay_payment_id", "razorpay_signature", "status"
        ])

        # Update order
        order = payment.order
        order.payment_status        = Order.PaymentStatus.PAID
        order.razorpay_payment_id   = razorpay_payment_id
        order.status                = Order.Status.CONFIRMED
        order.save(update_fields=[
            "payment_status", "razorpay_payment_id", "status"
        ])

        logger.info(
            "Payment verified for order %s — razorpay_payment_id: %s",
            order.id, razorpay_payment_id,
        )
        return payment

    @staticmethod
    def get_payment_history(user, params) -> tuple[list, int]:
        from .serializers import PaymentSerializer
        qs = (
            Payment.objects
            .filter(user=user)
            .select_related("order")
            .order_by("-created_at")
        )
        total  = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        return PaymentSerializer(sliced, many=True).data, total
