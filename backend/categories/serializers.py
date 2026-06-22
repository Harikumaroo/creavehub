"""
CraveHub — Categories Serializers
"""

from rest_framework import serializers
from .models import Category


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "icon", "emoji", "display_order"]
        read_only_fields = fields


class CategoryListSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "icon", "emoji", "display_order", "subcategories"]
        read_only_fields = fields


class CategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True, default=None)

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "image", "icon", "emoji",
            "display_order", "is_active", "parent", "parent_name",
            "subcategories", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "image", "icon", "emoji", "display_order", "is_active", "parent"]

    def validate_name(self, value: str) -> str:
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A category with this name already exists."
            )
        return value.strip().title()