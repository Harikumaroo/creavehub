"""
CraveHub Shared Validators
"""

import re
from django.core.exceptions import ValidationError


def validate_slug(value: str) -> None:
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Slug may only contain lowercase letters, digits, and hyphens."
        )


def validate_pincode(value: str) -> None:
    if not re.match(r"^\d{6}$", value):
        raise ValidationError("Pincode must be exactly 6 digits.")


def validate_phone_number(value: str) -> None:
    if not re.match(r"^\+?[1-9]\d{7,14}$", value):
        raise ValidationError("Enter a valid phone number.")


def validate_positive(value) -> None:
    if value <= 0:
        raise ValidationError("Value must be greater than zero.")


def validate_non_negative(value) -> None:
    if value < 0:
        raise ValidationError("Value must be zero or greater.")


def validate_percentage(value: float) -> None:
    if not (0 <= value <= 100):
        raise ValidationError("Percentage must be between 0 and 100.")


def validate_latitude(value: float) -> None:
    if not (-90 <= value <= 90):
        raise ValidationError("Latitude must be between -90 and 90.")


def validate_longitude(value: float) -> None:
    if not (-180 <= value <= 180):
        raise ValidationError("Longitude must be between -180 and 180.")


def validate_future_date(value) -> None:
    from django.utils import timezone
    if value <= timezone.now().date():
        raise ValidationError("Date must be in the future.")