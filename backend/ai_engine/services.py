"""
CraveHub — AI Engine Service Layer (Full Groq Integration)
Powered by Groq (llama-3.3-70b-versatile) — Ultra-fast AI inference

Features:
1. Smart Food Recommendations
2. Mood-Based Food Discovery
3. Natural Language Smart Search
4. AI Food Chat Support
5. Reorder Prediction
6. Smart Combo Generator
7. AI Offer Targeting
8. Food Nutrition Assistant
"""

from __future__ import annotations
import logging
from django.core.cache import cache
from .recommendation import RecommendationEngine

logger = logging.getLogger(__name__)
RECO_CACHE_TTL = 60 * 3  # 3 min


def _get_groq_client():
    """Return a Groq client (OpenAI-compatible) or None if no key configured."""
    try:
        from django.conf import settings
        import openai
        key = getattr(settings, 'GROQ_API_KEY', '')
        if not key:
            return None, None
        import httpx
        client = openai.OpenAI(
            api_key=key,
            base_url=getattr(settings, 'GROQ_BASE_URL', 'https://api.groq.com/openai/v1'),
            http_client=httpx.Client(),
        )
        model = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
        return client, model
    except Exception as e:
        logger.warning('Groq client init failed: %s', e)
        return None, None


def _groq_chat(system: str, user: str, max_tokens: int = 300, temperature: float = 0.6) -> str | None:
    """Helper: single Groq chat completion. Returns text or None."""
    client, model = _get_groq_client()
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning('Groq chat error: %s', e)
        return None


class AIService:

    # ─────────────────────────────────────────────────────────────
    # 1. SMART FOOD RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_recommendations(user, context: str = "home") -> dict:
        cache_key = f"cravehub:ai:reco:{user.id}:{context}"
        cached    = cache.get(cache_key)
        if cached:
            return cached
        result = RecommendationEngine.get_recommendations(user=user, context=context)
        cache.set(cache_key, result, RECO_CACHE_TTL)
        return result

    @staticmethod
    def invalidate_user_reco_cache(user) -> None:
        for ctx in ("home", "search", "post_order"):
            cache.delete(f"cravehub:ai:reco:{user.id}:{ctx}")

    # ─────────────────────────────────────────────────────────────
    # 2. MOOD-BASED FOOD DISCOVERY
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_mood_recommendations(mood: str) -> dict:
        """
        Given a mood, return AI-generated food category and dish suggestions.
        Moods: happy, sad, romantic, party, study, gaming, workout, family
        """
        cache_key = f"cravehub:ai:mood:{mood.lower()}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Fetch valid categories to ground the AI
        try:
            from categories.models import Category
            import random
            db_cats = list(Category.objects.values_list('name', flat=True).distinct())
            # Use up to 100 random categories to avoid hitting token limits while giving variety
            if len(db_cats) > 100:
                db_cats = random.sample(db_cats, 100)
            valid_categories = ", ".join(db_cats)
        except Exception:
            valid_categories = "Pizza, Biryani, Burgers, Chinese, Desserts, South Indian, North Indian, Snacks"

        system = f"""You are CraveHub's mood-based food recommendation AI.
Given a user's mood, suggest:
- 3-5 food categories (Pick ONLY from this list: {valid_categories})
- 5 to 10 specific dish names that belong to those chosen categories (maximum of 10 foods). Ensure these are common dishes found in those categories.
- A short mood-matching message (1 sentence, warm and fun)
- An emoji that matches the mood

Respond ONLY in this exact JSON format:
{{
  "categories": ["Category 1", "Category 2"],
  "dishes": ["Dish 1", "Dish 2", "Dish 3"],
  "message": "Comfort food incoming! These warm dishes will lift your spirits 🤗",
  "emoji": "🍕"
}}"""

        mood_context = {
            "happy": "User is happy and celebratory, wants something fun and indulgent",
            "sad": "User feels sad or down, needs comfort food to cheer them up",
            "romantic": "User is on a date or feeling romantic, wants elegant/special food",
            "party": "User is hosting or going to a party, needs party food and snacks",
            "study": "User is studying or working, needs brain food and energizing snacks",
            "gaming": "User is gaming, needs quick finger foods and energy drinks",
            "workout": "User just worked out or is health-conscious, wants high-protein healthy food",
            "family": "User is having family time, wants comfort food everyone can enjoy",
            "stressed": "User is stressed, needs comfort food that's soothing",
            "bored": "User is bored and wants to try something new and exciting",
            "angry": "User is angry, needs crunchy or heavily spiced food to let out steam",
        }

        user_msg = mood_context.get(mood.lower(), f"User is feeling {mood}")

        result_text = _groq_chat(system, user_msg, max_tokens=200, temperature=0.7)

        if result_text:
            try:
                import json
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result['mood'] = mood
                    result['ai_powered'] = True
                    cache.set(cache_key, result, 60 * 30)  # 30 min cache
                    return result
            except Exception as e:
                logger.warning('Mood recommendation parse error: %s', e)

        fallback = {
            "happy": {"categories": ["Pizza", "Desserts", "Burgers"], "dishes": ["Pepperoni Pizza", "Chocolate Brownie", "Loaded Burger", "Ice Cream Sundae", "Fries", "Cheesecake", "Nachos", "Donuts", "Tacos", "Milkshake"], "message": "Celebrate with your favourite treats! 🎉", "emoji": "😊"},
            "sad": {"categories": ["Biryani", "Ice Cream", "Chocolate"], "dishes": ["Comfort Biryani", "Butterscotch Ice Cream", "Hot Chocolate", "Mac & Cheese", "Ramen", "Brownie", "Mashed Potatoes", "Tomato Soup", "Grilled Cheese", "Pancakes"], "message": "Some comfort food will make you feel better 🤗", "emoji": "😔"},
            "romantic": {"categories": ["Italian", "Fine Dining", "Desserts"], "dishes": ["Pasta Carbonara", "Tiramisu", "Red Velvet Cake", "Steak", "Risotto", "Chocolate Fondue", "Wine", "Oysters", "Sushi", "Cheesecake"], "message": "Perfect dishes for a special evening ❤️", "emoji": "❤️"},
            "party": {"categories": ["Pizza", "Snacks", "Beverages"], "dishes": ["Party Pizza", "Nachos", "Spring Rolls", "Chicken Wings", "Sliders", "Chips and Dip", "Garlic Bread", "Mozzarella Sticks", "Coke", "Brownie Bites"], "message": "Let the party begin with amazing food! 🎊", "emoji": "🎉"},
            "study": {"categories": ["Coffee", "Sandwiches", "Wraps"], "dishes": ["Cappuccino", "Club Sandwich", "Veg Wrap", "Energy Bar", "Smoothie", "Almonds", "Oatmeal", "Green Tea", "Avocado Toast", "Dark Chocolate"], "message": "Brain food to keep you focused 📚", "emoji": "📚"},
            "gaming": {"categories": ["Burgers", "Fries", "Energy Drinks"], "dishes": ["Double Cheeseburger", "Loaded Fries", "Energy Drink", "Pizza Slices", "Chicken Nuggets", "Doritos", "Mountain Dew", "Hot Dogs", "Onion Rings", "Tacos"], "message": "Fuel up for your gaming session! 🎮", "emoji": "🎮"},
            "workout": {"categories": ["Healthy", "Protein", "Salads"], "dishes": ["Grilled Chicken", "Protein Bowl", "Caesar Salad", "Protein Shake", "Boiled Eggs", "Quinoa Salad", "Greek Yogurt", "Salmon", "Tofu Stir Fry", "Sweet Potato"], "message": "High-protein food for your fitness goals 💪", "emoji": "💪"},
            "family": {"categories": ["Biryani", "Indian", "Desserts"], "dishes": ["Family Biryani", "Dal Makhani", "Gulab Jamun", "Paneer Tikka", "Butter Chicken", "Naan", "Raita", "Samosa", "Ice Cream Family Pack", "Rasmalai"], "message": "Perfect food for family bonding time 👨‍👩‍👧‍👦", "emoji": "👨‍👩‍👧‍👦"},
            "tired": {"categories": ["Coffee", "Comfort", "Quick Bites"], "dishes": ["Strong Espresso", "Chicken Soup", "Maggie", "Toasted Sandwich", "Instant Noodles", "Croissant", "Hot Tea", "Biscuits", "Energy Drink", "Bowl of Cereal"], "message": "Rest up and recharge with some easy bites 🥱", "emoji": "🥱"},
            "adventurous": {"categories": ["Exotic", "Spicy", "Fusion"], "dishes": ["Spicy Sushi Roll", "Thai Curry", "Mexican Tacos", "Korean BBQ", "Dim Sum", "Ramen", "Falafel Wrap", "Tikka Masala", "Ceviche", "Jalapeno Poppers"], "message": "Time to explore some bold, new flavours! 🤠", "emoji": "🤠"},
            "chill": {"categories": ["Snacks", "Beverages", "Desserts"], "dishes": ["Popcorn", "Iced Tea", "Cookies", "Ice Cream", "Nachos", "Cold Coffee", "Brownie", "Potato Chips", "Lemonade", "Fruit Bowl"], "message": "Kick back and relax with some chill snacks 😎", "emoji": "😎"},
            "stressed": {"categories": ["Comfort", "Sweets", "Fast Food"], "dishes": ["Mac and Cheese", "Ice Cream Tub", "French Fries", "Dark Chocolate", "Pizza", "Cheeseburger", "Donuts", "Milkshake", "Fried Chicken", "Warm Brownie"], "message": "Take a deep breath and treat yourself 😫", "emoji": "😫"},
            "angry": {"categories": ["Spicy", "Crunchy", "Meat"], "dishes": ["Spicy Wings", "Crunchy Fried Chicken", "Jalapeno Poppers", "Spicy Ramen", "Chili Potato", "Nachos", "Burger", "Hot Tacos", "Vindaloo", "Sizzler"], "message": "Blow off some steam with these fiery and crunchy bites! 😠", "emoji": "😠"},
        }
        result = fallback.get(mood.lower(), fallback["happy"])
        result['mood'] = mood
        result['ai_powered'] = False
        return result

    # ─────────────────────────────────────────────────────────────
    # 3. SMART NATURAL LANGUAGE SEARCH
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def smart_search(query: str) -> dict:
        """
        Convert natural language query into structured search filters.
        e.g. "spicy chicken under ₹250" → {q: "chicken", max_price: 250, tags: ["spicy"]}
        """
        cache_key = f"cravehub:ai:search:{query.lower()[:60]}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        system = """You are CraveHub's smart search AI. Convert natural language food queries into structured search filters.

Respond ONLY in this exact JSON format:
{
  "search_query": "main food item to search",
  "max_price": null or number,
  "min_rating": null or number (1-5),
  "is_veg": null or true/false,
  "cuisine_type": null or "Indian/Chinese/Italian/etc",
  "tags": ["spicy", "healthy", "quick", etc],
  "time_filter": null or "fast" (under 30 min),
  "interpreted_as": "Human friendly explanation of what you understood"
}"""

        result_text = _groq_chat(system, f"User searched: {query}", max_tokens=200, temperature=0.2)

        if result_text:
            try:
                import json, re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result['original_query'] = query
                    result['ai_powered'] = True
                    cache.set(cache_key, result, 60 * 5)
                    return result
            except Exception as e:
                logger.warning('Smart search parse error: %s', e)

        return {
            "search_query": query,
            "original_query": query,
            "ai_powered": False,
            "interpreted_as": query,
        }

    # ─────────────────────────────────────────────────────────────
    # 4. AI FOOD CHAT (Support Bot)
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def food_chat(user, message: str, history: list) -> str:
        """
        Full AI-powered food assistant chat using Groq.
        Falls back to rule-based if no API key.
        """
        # Try Groq first
        try:
            client, model = _get_groq_client()
            if client:
                from . import prompts
                messages = [{"role": "system", "content": prompts.CHAT_SYSTEM_PROMPT_V2}]
                for h in (history or []):
                    role = h.get("role", "user")
                    if role in ("user", "assistant"):
                        messages.append({"role": role, "content": h.get("content", "")})
                messages.append({"role": "user", "content": message})

                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7,
                )
                return resp.choices[0].message.content
        except Exception as e:
            logger.warning('Groq chat failed: %s', e)

        return AIService._rule_based_chat(user, message)

    @staticmethod
    def _rule_based_chat(user, message: str) -> str:
        """Fallback rule-based responses."""
        msg = message.lower().strip()
        name = getattr(user, "full_name", "").split()[0] if getattr(user, "full_name", "") else "there"

        if any(w in msg for w in ("hello", "hi", "hey")):
            return f"Hey {name}! 👋 What are you craving today? I can help you find great food, track orders, or discover new restaurants! 🍽️"
        if any(w in msg for w in ("recommend", "suggest", "what should")):
            return "I'd recommend trying our trending biryanis tonight! 🔥 Check the 'Featured Picks' on your home screen for today's best restaurants."
        if any(w in msg for w in ("veg", "vegetarian")):
            return "We have amazing vegetarian options! 🥗 Use the 'Veg Only' filter to browse plant-based restaurants near you."
        if any(w in msg for w in ("track", "order", "status", "where is")):
            return "Head to the **Orders** tab to track your live order in real time 📦 You'll see the live map and estimated delivery time!"
        if any(w in msg for w in ("offer", "coupon", "discount", "promo")):
            return "Check **Today's Deals** on the home screen for the freshest coupons! 🏷️ Use the coupon code at checkout."
        if any(w in msg for w in ("spicy", "hot")):
            return "Love the heat! 🌶️ Search 'spicy' to find fiery dishes near you, or check our spicy food filter!"
        if any(w in msg for w in ("fast", "quick", "urgent", "asap")):
            return "In a hurry? ⚡ Sort restaurants by delivery time — look for the 'Fast Delivery' badge for orders under 30 minutes!"
        if any(w in msg for w in ("healthy", "diet", "protein", "calories")):
            return "Looking for healthy options? 💪 Filter by 'Healthy' or search for specific cuisines like salads, grilled items, or protein bowls!"
        if any(w in msg for w in ("budget", "cheap", "affordable", "under")):
            return "Finding budget-friendly meals? 💰 Use the price filter to set your max budget. We have great options starting from ₹50!"

        return "I'm your CraveHub AI assistant! 🤖 Ask me for food recommendations, help with your order, coupon codes, or to find the perfect restaurant for any occasion 😊"

    # ─────────────────────────────────────────────────────────────
    # 4b. SUPPORT TICKET CHAT (Customer Support AI)
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def support_chat(user, message: str, history: list, ticket_subject: str = "", ticket_category: str = "") -> str:
        """
        Dedicated AI support agent chat for Help & Support tickets.
        Uses SUPPORT_CHAT_SYSTEM_PROMPT — NOT the food assistant prompt.
        """
        try:
            client, model = _get_groq_client()
            if client:
                from . import prompts

                # Build context-aware system prompt with ticket info
                system_prompt = prompts.SUPPORT_CHAT_SYSTEM_PROMPT
                if ticket_subject or ticket_category:
                    context_note = "\n\nCURRENT TICKET CONTEXT:\n"
                    if ticket_subject:
                        context_note += f"- Issue subject: {ticket_subject}\n"
                    if ticket_category:
                        context_note += f"- Issue category: {ticket_category}\n"
                    context_note += "Use this context to give a relevant, focused response to the customer's issue."
                    system_prompt = system_prompt + context_note

                messages = [{"role": "system", "content": system_prompt}]
                for h in (history or []):
                    role = h.get("role", "user")
                    if role in ("user", "assistant"):
                        messages.append({"role": role, "content": h.get("content", "")})
                messages.append({"role": "user", "content": message})

                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=350,
                    temperature=0.5,
                )
                return resp.choices[0].message.content
        except Exception as e:
            logger.warning('Groq support_chat failed: %s', e)

        return AIService._rule_based_support_chat(user, message)

    @staticmethod
    def _rule_based_support_chat(user, message: str) -> str:
        """Fallback rule-based support responses (no AI key available)."""
        msg = message.lower().strip()
        name = getattr(user, "full_name", "").split()[0] if getattr(user, "full_name", "") else "there"

        if any(w in msg for w in ("hello", "hi", "hey")):
            return f"Hello {name}! I'm your CraveHub support assistant. I'm here to help resolve your issue. Please describe the problem you're facing and I'll do my best to assist you."
        if any(w in msg for w in ("refund", "money back", "return")):
            return "I understand you're requesting a refund. Eligible refunds are processed within 5-7 business days to your original payment method. I've noted your request — our support team will review and update you within 24 hours."
        if any(w in msg for w in ("not delivered", "missing", "not received", "where is my order")):
            return "I'm sorry to hear your order wasn't delivered. Please check the Orders tab for the latest status. If it still shows as 'out for delivery', our delivery partner may be nearby. I'm escalating this to our team for immediate attention."
        if any(w in msg for w in ("wrong item", "incorrect", "wrong food", "wrong order")):
            return "I sincerely apologize for receiving the wrong item. This is not acceptable and I'm escalating this issue to our team right away. You'll be contacted within 24 hours with a resolution — either a replacement or a full refund."
        if any(w in msg for w in ("cancel", "cancellation")):
            return "To cancel an order, go to the Orders tab, select your active order, and tap 'Cancel Order'. Note that cancellation may not be possible if the restaurant has already started preparing your food. If you need further help, our team will assist you."
        if any(w in msg for w in ("payment", "charged", "double charge", "payment failed")):
            return "I understand there's a payment concern. If you were double-charged, the extra amount will be automatically refunded within 5-7 business days. If your payment failed but was deducted, please share your order ID and I'll escalate this for you."
        if any(w in msg for w in ("late", "delay", "slow", "taking long")):
            return "I apologize for the delay. Please check the Orders tab for live tracking. If the estimated time has passed significantly, I'm raising this with our delivery team. You can also contact the delivery partner directly from the tracking screen."
        if any(w in msg for w in ("complaint", "bad experience", "terrible", "worst", "angry", "frustrated")):
            return f"I'm really sorry to hear about your experience, {name}. This is not the standard we aim for at CraveHub. I'm escalating your complaint to our senior support team — you'll receive a response within 24 hours. We sincerely apologize for the inconvenience."

        return "Thank you for reaching out to CraveHub Support. I'm reviewing your issue and will help resolve it as quickly as possible. Could you please provide more details about the problem you're experiencing? Is there anything else I can help you with?"


    # ─────────────────────────────────────────────────────────────
    # 5. REORDER PREDICTION
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_reorder_predictions(user) -> list:
        """
        Predict what the user is most likely to reorder based on their history.
        Returns top 3 predicted reorders.
        """
        try:
            from orders.models import Order
            import datetime

            recent_orders = (
                Order.objects
                .filter(user=user, status='delivered')
                .order_by('-created_at')
                .select_related('restaurant')
                .prefetch_related('items__menu_item')[:20]
            )

            if not recent_orders.exists():
                return []

            # Build order frequency map
            reorder_map = {}
            for order in recent_orders:
                key = str(order.restaurant_id)
                if key not in reorder_map:
                    reorder_map[key] = {
                        'restaurant_id': key,
                        'restaurant_name': order.restaurant.name if order.restaurant else 'Restaurant',
                        'count': 0,
                        'last_ordered': order.created_at,
                        'items': [],
                    }
                reorder_map[key]['count'] += 1
                for item in order.items.all()[:3]:
                    if hasattr(item, 'menu_item') and item.menu_item:
                        if item.menu_item.name not in reorder_map[key]['items']:
                            reorder_map[key]['items'].append(item.menu_item.name)

            # Sort by frequency
            sorted_predictions = sorted(reorder_map.values(), key=lambda x: x['count'], reverse=True)
            return sorted_predictions[:3]

        except Exception as e:
            logger.warning('Reorder prediction error: %s', e)
            return []

    # ─────────────────────────────────────────────────────────────
    # 6. AI SMART COMBO GENERATOR
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def generate_combo(main_item_name: str, restaurant_name: str = "") -> dict:
        """
        Given a main dish, AI suggests complementary items to form a combo.
        """
        cache_key = f"cravehub:ai:combo:{main_item_name.lower()[:40]}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        system = """You are CraveHub's smart combo generator AI.
Given a main food item, suggest 2-3 perfect complementary sides/drinks to form an ideal combo meal.

Respond ONLY in this exact JSON format:
{
  "main": "main item name",
  "sides": ["Side 1", "Side 2"],
  "drink": "Drink suggestion",
  "combo_name": "Creative combo name",
  "why": "One sentence explaining why this combo works great"
}"""

        result_text = _groq_chat(
            system,
            f"Main dish: {main_item_name}" + (f" from {restaurant_name}" if restaurant_name else ""),
            max_tokens=150,
            temperature=0.7,
        )

        if result_text:
            try:
                import json, re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result['ai_powered'] = True
                    cache.set(cache_key, result, 60 * 60)  # 1 hr cache
                    return result
            except Exception as e:
                logger.warning('Combo generator parse error: %s', e)

        return {
            "main": main_item_name,
            "sides": ["French Fries", "Coleslaw"],
            "drink": "Cold Drink",
            "combo_name": f"{main_item_name} Combo",
            "why": "A classic pairing that never disappoints!",
            "ai_powered": False,
        }

    # ─────────────────────────────────────────────────────────────
    # 7. AI OFFER TARGETING
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_personalized_offer(user) -> dict | None:
        """
        AI decides the best offer to show a specific user based on their profile.
        """
        try:
            profile = getattr(user, 'preference_profile', None)
            total_orders = getattr(profile, 'total_orders', 0) if profile else 0
            avg_order = float(getattr(profile, 'avg_order_value', 0) if profile else 0)
            fav_cuisines = getattr(profile, 'favourite_cuisines', []) if profile else []

            if total_orders == 0:
                return {
                    "code": "WELCOME50",
                    "title": "Welcome Gift! 🎁",
                    "description": "Flat ₹50 off on your first order",
                    "reason": "New user welcome offer",
                }
            elif total_orders >= 10 and avg_order >= 300:
                return {
                    "code": "VIP200",
                    "title": "VIP Reward! 👑",
                    "description": "Flat ₹200 off — You're a CraveHub VIP!",
                    "reason": "Loyalty reward for frequent high-value orders",
                }
            elif total_orders >= 1:
                cuisine = fav_cuisines[0].capitalize() if fav_cuisines else "Food"
                return {
                    "code": "CRAVE20",
                    "title": f"Your Favourite {cuisine}! 🍽️",
                    "description": f"20% off on {cuisine} orders above ₹200",
                    "reason": f"Personalized based on your love for {cuisine}",
                }
        except Exception as e:
            logger.warning('Offer targeting error: %s', e)
        return None

    # ─────────────────────────────────────────────────────────────
    # 8. FOOD NUTRITION ASSISTANT
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_nutrition_info(food_item: str) -> dict:
        """
        AI provides nutritional information for a food item.
        """
        cache_key = f"cravehub:ai:nutrition:{food_item.lower()[:40]}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        system = """You are a food nutrition expert AI for CraveHub.
Given a food item name, provide approximate nutritional information for a standard serving.

Respond ONLY in this exact JSON format:
{
  "food": "food name",
  "serving": "standard serving size",
  "calories": number,
  "protein": "Xg",
  "carbs": "Xg",
  "fat": "Xg",
  "is_healthy": true or false,
  "health_tip": "One short tip about this food (max 15 words)"
}"""

        result_text = _groq_chat(system, f"Nutrition info for: {food_item}", max_tokens=150, temperature=0.1)

        if result_text:
            try:
                import json, re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result['ai_powered'] = True
                    cache.set(cache_key, result, 60 * 60 * 24)  # 24hr cache
                    return result
            except Exception as e:
                logger.warning('Nutrition parse error: %s', e)

        return {
            "food": food_item,
            "serving": "1 serving",
            "calories": None,
            "ai_powered": False,
            "health_tip": "Nutritional data not available",
        }

    # ─────────────────────────────────────────────────────────────
    # 9. WEATHER-BASED FOOD RECOMMENDATION
    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_weather_recommendation(lat: float, lng: float) -> dict:
        """
        Fetches current weather via OpenWeatherMap (with Open-Meteo fallback)
        and uses Groq AI to suggest the perfect food.
        """
        cache_key = f"cravehub:ai:weather:v2:{round(lat, 2)}:{round(lng, 2)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Default fallback
        fallback = {
            "weather_title": "Cozy day detected ☁️",
            "food_name": "Hot Coffee & Snacks",
            "reason": "Perfect for this weather!",
            "tag": "Weather Special",
            "tag_emoji": "☁️",
            "ai_powered": False
        }

        try:
            import requests
            
            condition = "Clear"
            temp = 25
            
            # Try OpenWeatherMap First
            owm_key = "87b9eea0a71cca44e9f873f8ff704e95"
            owm_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={owm_key}&units=metric"
            logger.info('Weather: Calling OpenWeatherMap for lat=%s lng=%s', lat, lng)
            owm_resp = requests.get(owm_url, timeout=8)
            logger.info('Weather: OpenWeatherMap status=%s', owm_resp.status_code)
            
            if owm_resp.status_code == 200:
                data = owm_resp.json()
                temp = data.get("main", {}).get("temp", 25)
                weather_arr = data.get("weather", [])
                if weather_arr:
                    condition = weather_arr[0].get("main", "Clear")
                logger.info('Weather: Got condition=%s temp=%s from OpenWeatherMap', condition, temp)
            else:
                logger.warning('Weather: OpenWeatherMap failed (%s), falling back to Open-Meteo', owm_resp.status_code)
                # Fallback to Open-Meteo if OpenWeatherMap key is inactive/invalid
                om_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,weather_code"
                om_resp = requests.get(om_url, timeout=8)
                if om_resp.status_code == 200:
                    data = om_resp.json()
                    current = data.get("current", {})
                    temp = current.get("temperature_2m", 25)
                    code = current.get("weather_code", 0)

                    if code in [1, 2, 3]: condition = "Cloudy"
                    elif code in [45, 48]: condition = "Foggy"
                    elif 51 <= code <= 67 or code >= 80: condition = "Rainy"
                    elif 71 <= code <= 77: condition = "Snowy"
                    elif code >= 95: condition = "Stormy"
                    logger.info('Weather: Got condition=%s temp=%s from Open-Meteo', condition, temp)

            weather_desc = f"{condition} with a temperature of {temp}°C"
            logger.info('Weather: Sending to Groq AI: %s', weather_desc)

            system = f"""You are CraveHub's weather-based food recommendation AI.
Given the current local weather, suggest ONE perfect food item that people crave in this weather.

Respond ONLY in this exact JSON format:
{{
  "weather_title": "Short title describing the {condition} weather",
  "food_name": "Name of the dish",
  "search_term": "A single core keyword for searching the menu",
  "reason": "Short reason why it fits the {condition} weather",
  "tag": "Short tag about the weather",
  "tag_emoji": "emoji"
}}"""

            # Direct Groq API call via requests (bypasses openai library httpx issue)
            from django.conf import settings as django_settings
            groq_key = getattr(django_settings, 'GROQ_API_KEY', '')
            groq_model = getattr(django_settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
            
            if groq_key:
                groq_resp = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {groq_key}',
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': groq_model,
                        'messages': [
                            {'role': 'system', 'content': system},
                            {'role': 'user', 'content': f'Current weather: {weather_desc}'},
                        ],
                        'max_tokens': 150,
                        'temperature': 0.7,
                    },
                    timeout=10,
                )
                logger.info('Weather: Groq API status=%s', groq_resp.status_code)
                
                if groq_resp.status_code == 200:
                    groq_data = groq_resp.json()
                    result_text = groq_data['choices'][0]['message']['content']
                    logger.info('Weather: Groq AI response received')

                    import json, re
                    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                        result['ai_powered'] = True
                        result['temp'] = temp
                        result['condition'] = condition
                        cache.set(cache_key, result, 60 * 30)
                        logger.info('Weather: Returning AI result: %s', result.get('food_name'))
                        return result
                    else:
                        logger.warning('Weather: No JSON found in Groq response: %s', result_text[:100])
                else:
                    logger.warning('Weather: Groq API error %s: %s', groq_resp.status_code, groq_resp.text[:200])
            else:
                logger.warning('Weather: No GROQ_API_KEY configured')
        except Exception as e:
            logger.error('Weather recommendation error: %s', e, exc_info=True)

        logger.warning('Weather: Returning fallback')
        return fallback

# force auto-reload to clear memory cache
# auto-reload for httpx downgrade
