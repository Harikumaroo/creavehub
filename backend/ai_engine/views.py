"""
CraveHub — AI Engine Views (Full Groq Integration)

Endpoints:
  GET  /api/v1/ai/recommendations/         → Personalized food recommendations
  POST /api/v1/ai/chat/                    → AI food assistant chat
  POST /api/v1/ai/agent/                   → AI Agent — full app access (function calling)
  GET  /api/v1/ai/mood/?mood=happy         → Mood-based food discovery
  POST /api/v1/ai/smart-search/            → Natural language search conversion
  GET  /api/v1/ai/reorder/                 → Reorder predictions
  POST /api/v1/ai/combo/                   → Smart combo generator
  GET  /api/v1/ai/offer/                   → Personalized offer targeting
  GET  /api/v1/ai/nutrition/?item=pizza    → Food nutrition info
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from core.helpers import error_response, success_response
from core.permissions import IsAuthenticatedAndActive, AllowAny

from .serializers import ChatMessageSerializer, RecommendationSerializer
from .services import AIService


class RecommendationView(APIView):
    """
    GET /api/v1/ai/recommendations/?context=home
    Returns personalised restaurant + menu item recommendations.
    context: home | search | post_order
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        serializer = RecommendationSerializer(data=request.query_params)
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors)
        result = AIService.get_recommendations(
            user=request.user,
            context=serializer.validated_data.get("context", "home"),
        )
        return success_response(data=result, message="Recommendations fetched successfully")


class FoodChatView(APIView):
    """
    POST /api/v1/ai/chat/
    AI-powered food assistant chatbot (Groq llama-3.3-70b-versatile).
    Body: {"message": "...", "history": [{"role": "user", "content": "..."}]}
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation failed", errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        reply = AIService.food_chat(
            user=request.user,
            message=serializer.validated_data["message"],
            history=serializer.validated_data.get("history", []),
        )
        return success_response(
            data={"reply": reply, "role": "assistant"},
            message="Response generated",
        )


class MoodFoodView(APIView):
    """
    GET /api/v1/ai/mood/?mood=happy
    Returns AI mood-based food recommendations.
    Moods: happy, sad, romantic, party, study, gaming, workout, family, stressed, bored
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        mood = request.query_params.get("mood", "happy").strip().lower()
        if not mood:
            return error_response("Mood parameter is required")
        result = AIService.get_mood_recommendations(mood=mood)
        return success_response(data=result, message="Mood recommendations fetched")


class SmartSearchView(APIView):
    """
    POST /api/v1/ai/smart-search/
    Convert natural language search into structured filters.
    Body: {"query": "spicy chicken under 250"}
    """
    permission_classes = [AllowAny]

    def post(self, request: Request):
        query = request.data.get("query", "").strip()
        if not query:
            return error_response("Search query is required")
        result = AIService.smart_search(query=query)
        return success_response(data=result, message="Smart search processed")


class ReorderPredictionView(APIView):
    """
    GET /api/v1/ai/reorder/
    Returns AI-predicted reorder suggestions for the authenticated user.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        predictions = AIService.get_reorder_predictions(user=request.user)
        return success_response(
            data={"predictions": predictions},
            message="Reorder predictions fetched",
        )


class ComboGeneratorView(APIView):
    """
    POST /api/v1/ai/combo/
    AI generates a smart food combo for a given main item.
    Body: {"item": "Chicken Burger", "restaurant": "KFC"}
    """
    permission_classes = [AllowAny]

    def post(self, request: Request):
        item = request.data.get("item", "").strip()
        restaurant = request.data.get("restaurant", "").strip()
        if not item:
            return error_response("Item name is required")
        result = AIService.generate_combo(main_item_name=item, restaurant_name=restaurant)
        return success_response(data=result, message="Combo generated")


class PersonalizedOfferView(APIView):
    """
    GET /api/v1/ai/offer/
    Returns the most relevant personalized offer for the authenticated user.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        offer = AIService.get_personalized_offer(user=request.user)
        return success_response(
            data={"offer": offer},
            message="Personalized offer fetched",
        )


class NutritionAssistantView(APIView):
    """
    GET /api/v1/ai/nutrition/?item=biryani
    Returns AI-generated nutritional info for any food item.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        item = request.query_params.get("item", "").strip()
        if not item:
            return error_response("Food item parameter is required")
        result = AIService.get_nutrition_info(food_item=item)
        return success_response(data=result, message="Nutrition info fetched")


class AIAgentView(APIView):
    """
    POST /api/v1/ai/agent/
    Full AI Agent with function calling — can cancel orders, track orders,
    search food, manage cart, get offers, and reorder.
    Body: {"message": "...", "history": [...], "confirmed_action": null|"cancel_order"|"reorder"}
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        from .serializers import ChatMessageSerializer
        from .agent import AIAgent

        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors)

        result = AIAgent.run_agent(
            user=request.user,
            message=serializer.validated_data.get("message", ""),
            history=serializer.validated_data.get("history", []),
            image_base64=serializer.validated_data.get("image_base64"),
        )
        return success_response(data=result, message="Agent response")


class WeatherFoodView(APIView):
    """
    GET /api/v1/ai/weather-food/?lat=13.08&lng=80.27
    Returns AI food recommendations based on current local weather.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        try:
            lat = float(request.query_params.get("lat"))
            lng = float(request.query_params.get("lng"))
        except (TypeError, ValueError):
            return error_response("Valid lat and lng query parameters are required")

        result = AIService.get_weather_recommendation(lat=lat, lng=lng)
        return success_response(data=result, message="Weather recommendations fetched")
