"""
CraveHub Custom Exception Hierarchy
"""

from rest_framework import status


class CraveHubBaseException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message: str = "An unexpected error occurred."
    default_error_code: str = "INTERNAL_ERROR"

    def __init__(self, message=None, error_code=None, extra=None):
        self.message = message or self.default_message
        self.error_code = error_code or self.default_error_code
        self.extra = extra or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "success": False,
            "message": self.message,
            "error_code": self.error_code,
            **({"errors": self.extra} if self.extra else {}),
        }


class ValidationError(CraveHubBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Validation failed."
    default_error_code = "VALIDATION_ERROR"


class BadRequestError(CraveHubBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Bad request."
    default_error_code = "BAD_REQUEST"


class AuthenticationError(CraveHubBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Authentication credentials were not provided or are invalid."
    default_error_code = "AUTHENTICATION_REQUIRED"


class PermissionDeniedError(CraveHubBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "You do not have permission to perform this action."
    default_error_code = "PERMISSION_DENIED"


class NotFoundError(CraveHubBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "The requested resource was not found."
    default_error_code = "NOT_FOUND"


class CategoryNotFoundError(NotFoundError):
    default_message = "Category not found."
    default_error_code = "CATEGORY_NOT_FOUND"


class RestaurantNotFoundError(NotFoundError):
    default_message = "Restaurant not found."
    default_error_code = "RESTAURANT_NOT_FOUND"


class MenuNotFoundError(NotFoundError):
    default_message = "Menu item not found."
    default_error_code = "MENU_ITEM_NOT_FOUND"


class BannerNotFoundError(NotFoundError):
    default_message = "Banner not found."
    default_error_code = "BANNER_NOT_FOUND"


class OfferNotFoundError(NotFoundError):
    default_message = "Offer not found."
    default_error_code = "OFFER_NOT_FOUND"


class ConflictError(CraveHubBaseException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "A conflict occurred with the current state of the resource."
    default_error_code = "CONFLICT"


class RateLimitError(CraveHubBaseException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Too many requests. Please try again later."
    default_error_code = "RATE_LIMIT_EXCEEDED"


class ServiceUnavailableError(CraveHubBaseException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_message = "The service is temporarily unavailable."
    default_error_code = "SERVICE_UNAVAILABLE"

class OrderNotFoundError(NotFoundError):
    default_message = "Order not found."
    default_error_code = "ORDER_NOT_FOUND"


class PaymentError(CraveHubBaseException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_message = "Payment processing failed."
    default_error_code = "PAYMENT_ERROR"


class OrderCancellationError(BadRequestError):
    default_message = "Order cannot be cancelled."
    default_error_code = "ORDER_CANCELLATION_ERROR"
