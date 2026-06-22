"""
CraveHub — Core Serializers
"""

from rest_framework import serializers
from .models import AppSector


class AppSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSector
        fields = [
            "id", "name", "emoji",
            "bg_gradient_start", "bg_gradient_end",
            "border_color", "route", "display_order",
        ]
