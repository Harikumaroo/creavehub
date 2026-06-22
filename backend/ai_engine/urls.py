from django.urls import path
from .views import (
    RecommendationView,
    FoodChatView,
    MoodFoodView,
    SmartSearchView,
    ReorderPredictionView,
    ComboGeneratorView,
    PersonalizedOfferView,
    NutritionAssistantView,
    AIAgentView,
    WeatherFoodView,
)

app_name = "ai_engine"

urlpatterns = [
    path("recommendations/",  RecommendationView.as_view(),     name="recommendations"),
    path("chat/",             FoodChatView.as_view(),            name="chat"),
    path("agent/",            AIAgentView.as_view(),             name="agent"),
    path("mood/",             MoodFoodView.as_view(),            name="mood"),
    path("smart-search/",     SmartSearchView.as_view(),         name="smart_search"),
    path("reorder/",          ReorderPredictionView.as_view(),   name="reorder"),
    path("combo/",            ComboGeneratorView.as_view(),      name="combo"),
    path("offer/",            PersonalizedOfferView.as_view(),   name="offer"),
    path("nutrition/",        NutritionAssistantView.as_view(),  name="nutrition"),
    path("weather-food/",     WeatherFoodView.as_view(),         name="weather_food"),
]
