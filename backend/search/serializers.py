from rest_framework import serializers
from restaurants.serializers import RestaurantListSerializer
from menu.serializers import MenuItemSerializer
from .models import SearchHistory


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = SearchHistory
        fields = ["id", "query", "created_at"]


class UnifiedSearchResultSerializer(serializers.Serializer):
    """Wraps both restaurant and menu item results in one response."""
    restaurants = RestaurantListSerializer(many=True)
    menu_items  = MenuItemSerializer(many=True)
    query       = serializers.CharField()
    total_restaurants = serializers.IntegerField()
    total_menu_items  = serializers.IntegerField()
