from rest_framework import serializers
from .models import RestaurantReview, MenuItemReview


class RestaurantReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = RestaurantReview
        fields = ["id", "user", "user_name", "restaurant", "order", "rating", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]


class CreateRestaurantReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantReview
        fields = ["restaurant", "order", "rating", "comment"]

    def validate(self, attrs):
        user = self.context["request"].user
        if RestaurantReview.objects.filter(user=user, restaurant=attrs["restaurant"]).exists():
            raise serializers.ValidationError("You have already reviewed this restaurant.")
        # Ensure the order belongs to the user and is delivered
        order = attrs.get("order")
        if order:
            if order.user != user:
                raise serializers.ValidationError({"order": "Invalid order."})
            if order.status != "delivered":
                raise serializers.ValidationError({"order": "You can only review delivered orders."})
        return attrs


class MenuItemReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = MenuItemReview
        fields = ["id", "user", "user_name", "menu_item", "order", "rating", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]


class CreateMenuItemReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemReview
        fields = ["menu_item", "order", "rating", "comment"]

    def validate(self, attrs):
        user = self.context["request"].user
        if MenuItemReview.objects.filter(user=user, menu_item=attrs["menu_item"]).exists():
            raise serializers.ValidationError("You have already reviewed this item.")
        return attrs
