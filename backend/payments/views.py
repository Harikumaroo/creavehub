"""
CraveHub — Payments Views (Phase 3)
"""

from rest_framework import status, serializers, viewsets
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from django.conf import settings

from core.exceptions import CraveHubBaseException
from core.helpers import created_response, error_response, paginated_response, success_response
from core.helpers.pagination import PaginationParams
from core.permissions import IsAuthenticatedAndActive

from .serializers import InitiatePaymentSerializer, VerifyPaymentSerializer, SavedPaymentMethodSerializer
from .services import PaymentService
from .models import Payment, SavedPaymentMethod


class InitiatePaymentView(APIView):
    """
    POST /api/v1/payments/initiate/
    Creates a Razorpay order and returns credentials for the frontend SDK.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        try:
            data = PaymentService.initiate_payment(
                user=request.user,
                order_id=str(serializer.validated_data["order_id"]),
            )
            return created_response(data=data, message="Payment initiated successfully")
        except CraveHubBaseException as exc:
            return error_response(exc.message, error_code=exc.error_code, status_code=exc.status_code)
        except Exception as exc:
            return error_response(str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentView(APIView):
    """
    POST /api/v1/payments/verify/
    Verifies Razorpay signature and marks order as PAID.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = VerifyPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        try:
            payment = PaymentService.verify_payment(
                user=request.user,
                **serializer.validated_data,
            )
            from .serializers import PaymentSerializer
            return success_response(
                data=PaymentSerializer(payment).data,
                message="Payment verified successfully",
            )
        except CraveHubBaseException as exc:
            return error_response(exc.message, error_code=exc.error_code, status_code=exc.status_code)
        except Exception as exc:
            return error_response(str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentHistoryView(APIView):
    """
    GET /api/v1/payments/history/
    Returns paginated payment history for the authenticated user.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        params = PaginationParams.from_request(request)
        data, total = PaymentService.get_payment_history(user=request.user, params=params)
        return paginated_response(
            data=data, page=params.page, page_size=params.page_size,
            total_count=total, message="Payment history fetched successfully"
        )


class DevSimulatePaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()


class DevSimulatePaymentView(APIView):
    """
    POST /api/v1/payments/dev/simulate/
    Development-only endpoint to simulate a Razorpay successful payment.
    Enabled only when settings.DEBUG is True. Restricted to admin users.
    """
    permission_classes = [IsAdminUser]

    def post(self, request: Request):
        if not getattr(settings, "DEBUG", False):
            return error_response("Dev simulate endpoint disabled in production.", status_code=status.HTTP_403_FORBIDDEN)

        serializer = DevSimulatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        rz_order_id = serializer.validated_data["razorpay_order_id"]

        try:
            payment = Payment.objects.get(razorpay_order_id=rz_order_id)
        except Payment.DoesNotExist:
            return error_response("Payment not found", status_code=status.HTTP_404_NOT_FOUND)

        import uuid
        fake_payment_id = f"dev_pay_{uuid.uuid4().hex[:24]}"
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not key_secret:
            return error_response("RAZORPAY_KEY_SECRET not configured", status_code=status.HTTP_400_BAD_REQUEST)

        message = f"{rz_order_id}|{fake_payment_id}".encode("utf-8")
        import hashlib, hmac as _hmac
        generated_signature = _hmac.new(key_secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

        try:
            paid = PaymentService.verify_payment(
                user=payment.user,
                razorpay_order_id=rz_order_id,
                razorpay_payment_id=fake_payment_id,
                razorpay_signature=generated_signature,
            )
            from .serializers import PaymentSerializer
            return success_response(data=PaymentSerializer(paid).data, message="Simulated payment verified")
        except CraveHubBaseException as exc:
            return error_response(exc.message, error_code=exc.error_code, status_code=exc.status_code)


class SavedPaymentMethodViewSet(viewsets.ModelViewSet):
    """
    CRUD for Saved Payment Methods.
    """
    serializer_class = SavedPaymentMethodSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def get_queryset(self):
        return SavedPaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
