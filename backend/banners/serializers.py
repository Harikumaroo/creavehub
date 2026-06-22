"""
CraveHub — Banners Serializers
"""

from rest_framework import serializers
from .models import Banner


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "id", "title", "subtitle", "image",
            "redirect_url", "priority", "start_date", "end_date",
        ]
        read_only_fields = fields