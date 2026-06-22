"""
CraveHub — AI Agent Service
Full app access via Groq function calling.

The agent can:
- Get user's orders and order details
- Cancel orders (with reason)
- Track current order status
- Search restaurants and food
- Get cart contents
- Recommend food
- Answer food questions
"""
from __future__ import annotations
import json
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ── Tool Definitions (Groq function calling schema) ──────────────
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_my_orders",
            "description": "Get the user's recent orders. Use when user asks about their orders, order history, or current order status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by order status: pending, confirmed, preparing, out_for_delivery, delivered, cancelled. Leave empty for all orders.",
                        "enum": ["pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled", ""]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancel a specific order. Only works for orders in pending or confirmed status. ALWAYS confirm with user before cancelling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The UUID of the order to cancel"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation"
                    }
                },
                "required": ["order_id", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Get live tracking status for a specific order. Use when user asks 'where is my order', 'track my order', 'order status'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The UUID of the order to track. If not specified, track the most recent active order."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_catalog",
            "description": "Search for restaurants, food items, groceries, gifts, party packages, and catering menus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term e.g. 'biryani', 'chocolate gift', 'birthday party', 'buffet'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "Get the user's current cart contents and total.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_offers",
            "description": "Get available coupon codes and offers for the user.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reorder",
            "description": "Reorder items from a previous order. Ask user to confirm before reordering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The UUID of the previous order to reorder from"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_menu",
            "description": "Get the menu for a specific restaurant by its name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "The name of the restaurant to fetch the menu for (e.g. 'Trattoria Bella Vita')"
                    }
                },
                "required": ["restaurant_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_table",
            "description": "Book a table for dining at a restaurant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "The name of the restaurant"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g. 2026-06-19 for today)"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time in HH:MM:SS format (e.g. 20:00:00 for 8 PM)"
                    },
                    "guest_count": {
                        "type": "integer",
                        "description": "Number of guests"
                    },
                    "special_requests": {
                        "type": "string",
                        "description": "Any special requests"
                    }
                },
                "required": ["restaurant_name", "date", "time", "guest_count"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a specific menu item to the user's cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "The name of the restaurant"
                    },
                    "item_name": {
                        "type": "string",
                        "description": "The name of the food item to add"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity to add"
                    }
                },
                "required": ["restaurant_name", "item_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checkout_cart",
            "description": "Checkout the current cart and place the order.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


AGENT_SYSTEM_PROMPT = """You are CraveHub AI Agent — a smart assistant for the CraveHub app, handling Food Delivery, Instamart (Groceries & Gifts), Dineout, Parties, and Catering.

CAPABILITIES:
- You can view the user's orders and track live order status.
- You can cancel orders. ALWAYS ask for explicit user confirmation before cancelling.
- You can search for restaurants, food items, groceries, gifts, party packages, and catering menus.
- You can check the user's cart, add food items to cart, checkout cart, and get available offers/coupons.
- You can reorder from past orders. ALWAYS ask for explicit user confirmation before reordering.
- You can book a table for dining at a restaurant.

BEHAVIOR:
- Be warm, helpful and passionate about food and services.
- When you retrieve data, present it clearly.
- For tracking, give the current status and estimated time clearly.
- Keep responses concise — 2-4 sentences, use emojis sparingly.
- If user says "yes", "confirm", "go ahead", "do it" after you asked for confirmation — then proceed with the action.
- IMPORTANT: Use the provided functions natively to perform actions. Do NOT output raw function tags in your response text.
"""


class AIAgent:

    @staticmethod
    def execute_tool(tool_name: str, args: dict, user) -> dict:
        """Execute a tool call and return the result."""
        try:
            if tool_name == "get_my_orders":
                return AIAgent._get_orders(user, args.get("status", ""))

            elif tool_name == "cancel_order":
                return AIAgent._cancel_order(user, args.get("order_id"), args.get("reason", "Cancelled via AI"))

            elif tool_name == "track_order":
                return AIAgent._track_order(user, args.get("order_id"))

            elif tool_name == "search_catalog":
                return AIAgent._search_catalog(args.get("query", ""))

            elif tool_name == "get_cart":
                return AIAgent._get_cart(user)

            elif tool_name == "get_offers":
                return AIAgent._get_offers()

            elif tool_name == "reorder":
                return AIAgent._reorder(user, args.get("order_id"))

            elif tool_name == "get_restaurant_menu":
                return AIAgent._get_restaurant_menu(args.get("restaurant_name"))

            elif tool_name == "book_table":
                return AIAgent._book_table(
                    user,
                    args.get("restaurant_name"),
                    args.get("date"),
                    args.get("time"),
                    args.get("guest_count", 2),
                    args.get("special_requests", "")
                )

            elif tool_name == "add_to_cart":
                return AIAgent._add_to_cart(
                    user,
                    args.get("restaurant_name"),
                    args.get("item_name"),
                    args.get("quantity", 1)
                )

            elif tool_name == "checkout_cart":
                return AIAgent._checkout_cart(user)

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.warning("Agent tool %s failed: %s", tool_name, e)
            return {"error": str(e)}

    @staticmethod
    def _get_orders(user, status_filter: str = "") -> dict:
        from orders.models import Order
        from orders.serializers import OrderListSerializer
        qs = Order.objects.filter(user=user).select_related("restaurant").prefetch_related("items__menu_item").order_by("-created_at")
        if status_filter:
            qs = qs.filter(status=status_filter)
        orders = qs[:5]
        data = []
        for o in orders:
            items_summary = ", ".join([f"{i.quantity}x {i.name}" for i in o.items.all()[:3]])
            data.append({
                "order_id": str(o.id),
                "order_number": str(o.id)[:8].upper(),
                "restaurant": o.restaurant.name if o.restaurant else "Unknown",
                "status": o.status,
                "status_display": o.get_status_display(),
                "total": f"₹{o.grand_total}",
                "items": items_summary,
                "is_cancellable": o.is_cancellable,
                "placed_at": o.created_at.strftime("%d %b, %I:%M %p"),
            })
        return {"orders": data, "count": len(data)}

    @staticmethod
    def _cancel_order(user, order_id: str, reason: str) -> dict:
        from orders.models import Order
        try:
            order = Order.objects.get(id=order_id, user=user)
            if not order.is_cancellable:
                return {
                    "success": False,
                    "message": f"Order cannot be cancelled. Current status: {order.get_status_display()}. Orders can only be cancelled when Pending or Confirmed."
                }
            from django.utils import timezone
            order.status = Order.Status.CANCELLED
            order.cancel_reason = reason
            order.cancelled_at = timezone.now()
            order.save()
            return {
                "success": True,
                "message": f"Order #{str(order_id)[:8].upper()} from {order.restaurant.name if order.restaurant else 'restaurant'} has been cancelled successfully. Refund (if applicable) will be processed within 5-7 business days.",
                "order_id": order_id,
            }
        except Order.DoesNotExist:
            return {"success": False, "message": "Order not found or doesn't belong to your account."}

    @staticmethod
    def _track_order(user, order_id: str = None) -> dict:
        from orders.models import Order
        try:
            if order_id:
                order = Order.objects.get(id=order_id, user=user)
            else:
                # Get most recent active order
                order = Order.objects.filter(
                    user=user,
                    status__in=["pending", "confirmed", "preparing", "out_for_delivery"]
                ).select_related("restaurant").order_by("-created_at").first()

            if not order:
                return {"found": False, "message": "No active orders found. Your recent orders may have already been delivered."}

            status_messages = {
                "pending": "⏳ Waiting for restaurant to confirm",
                "confirmed": "✅ Restaurant has confirmed your order",
                "preparing": "👨‍🍳 Chef is preparing your food",
                "out_for_delivery": "🛵 Delivery partner is on the way!",
                "delivered": "🎉 Order delivered!",
                "cancelled": "❌ Order was cancelled",
            }

            return {
                "found": True,
                "order_id": str(order.id),
                "order_number": str(order.id)[:8].upper(),
                "restaurant": order.restaurant.name if order.restaurant else "Restaurant",
                "status": order.status,
                "status_message": status_messages.get(order.status, order.get_status_display()),
                "eta": f"{order.estimated_delivery_time} minutes" if order.estimated_delivery_time else "30-45 minutes",
                "total": f"₹{order.grand_total}",
                "placed_at": order.created_at.strftime("%d %b, %I:%M %p"),
                "is_cancellable": order.is_cancellable,
            }
        except Order.DoesNotExist:
            return {"found": False, "message": "Order not found."}

    @staticmethod
    def _search_catalog(query: str) -> dict:
        from restaurants.models import Restaurant
        from menu.models import MenuItem
        from instamart.models import InstamartProduct
        from catering.models import CateringMenu
        from parties.models import PartyPackage
        from django.db.models import Q

        restaurants = list(Restaurant.objects.filter(Q(name__icontains=query) | Q(description__icontains=query), is_active=True, is_deleted=False).values("id", "name", "rating", "delivery_time_min")[:3])
        food_items = list(MenuItem.objects.filter(Q(name__icontains=query), is_available=True).select_related("restaurant").values("name", "effective_price", "restaurant__name")[:3])
        instamart_items = list(InstamartProduct.objects.filter(Q(name__icontains=query), is_available=True).select_related("store").values("name", "price", "store__name")[:3])
        catering = list(CateringMenu.objects.filter(Q(name__icontains=query), is_active=True).select_related("restaurant").values("name", "price_per_plate", "restaurant__name")[:3])
        parties = list(PartyPackage.objects.filter(Q(name__icontains=query), is_active=True).select_related("restaurant").values("name", "price_per_person", "restaurant__name")[:3])

        return {
            "query": query,
            "restaurants": [{"name": r["name"], "rating": str(r.get("rating", "4.0")), "delivery_time": f"{r.get('delivery_time_min', 30)} min"} for r in restaurants],
            "food_dishes": [{"name": i["name"], "price": f"₹{i['effective_price']}", "provider": i["restaurant__name"]} for i in food_items],
            "instamart_products": [{"name": i["name"], "price": f"₹{i['price']}", "provider": i["store__name"]} for i in instamart_items],
            "catering_menus": [{"name": i["name"], "price": f"₹{i['price_per_plate']}/plate", "provider": i["restaurant__name"]} for i in catering],
            "party_packages": [{"name": i["name"], "price": f"₹{i['price_per_person']}/person", "provider": i["restaurant__name"]} for i in parties],
        }

    @staticmethod
    def _get_cart(user) -> dict:
        from cart.models import Cart
        try:
            cart = Cart.objects.filter(user=user).prefetch_related("items__menu_item__restaurant").first()
            if not cart or not cart.items.exists():
                return {"empty": True, "message": "Your cart is empty."}
            items = []
            total = 0
            for item in cart.items.all():
                price = float(item.menu_item.effective_price) * item.quantity
                total += price
                items.append({
                    "name": item.menu_item.name,
                    "quantity": item.quantity,
                    "price": f"₹{price:.0f}",
                    "restaurant": item.menu_item.restaurant.name if item.menu_item.restaurant else "",
                })
            return {"empty": False, "items": items, "total": f"₹{total:.0f}", "item_count": len(items)}
        except Exception as e:
            return {"empty": True, "error": str(e)}

    @staticmethod
    def _get_offers() -> dict:
        from offers.models import Offer
        offers = list(Offer.objects.filter(is_active=True).values("code", "title", "description", "discount_value", "discount_type")[:5])
        return {
            "offers": [{"code": o["code"], "title": o.get("title", o["code"]), "description": o.get("description", ""), "discount": f"{o['discount_value']}{'%' if o['discount_type'] == 'percentage' else '₹ off'}"} for o in offers]
        }

    @staticmethod
    def _reorder(user, order_id: str) -> dict:
        from orders.models import Order
        from cart.models import Cart, CartItem
        from menu.models import MenuItem
        try:
            order = Order.objects.get(id=order_id, user=user)
            # Clear cart and re-add items
            Cart.objects.filter(user=user).delete()
            cart = Cart.objects.create(user=user)
            added = []
            for item in order.items.all():
                try:
                    menu_item = MenuItem.objects.get(id=item.menu_item_id, is_available=True)
                    CartItem.objects.create(cart=cart, menu_item=menu_item, quantity=item.quantity)
                    added.append(item.name)
                except MenuItem.DoesNotExist:
                    pass
            if added:
                return {"success": True, "message": f"Added {len(added)} items to your cart from your previous order at {order.restaurant.name if order.restaurant else 'the restaurant'}. Items: {', '.join(added[:3])}. Go to cart to place the order!", "items_added": added}
            return {"success": False, "message": "Could not re-add items — some items may no longer be available."}
        except Order.DoesNotExist:
            return {"success": False, "message": "Order not found."}

    @staticmethod
    def _get_restaurant_menu(restaurant_name: str) -> dict:
        from restaurants.models import Restaurant
        from menu.models import MenuItem
        from django.db.models import Q

        # Find closest matching restaurant
        restaurant = Restaurant.objects.filter(name__icontains=restaurant_name, is_active=True, is_deleted=False).first()
        if not restaurant:
            return {"found": False, "message": f"Could not find a restaurant named '{restaurant_name}'"}

        # Get top 8 menu items
        items = list(
            MenuItem.objects.filter(restaurant=restaurant, is_available=True)
            .values("name", "effective_price", "description", "is_veg")[:8]
        )
        return {
            "found": True,
            "restaurant_name": restaurant.name,
            "items": [{"name": i["name"], "price": f"₹{i['effective_price']}", "description": i.get("description", ""), "is_veg": i["is_veg"]} for i in items]
        }

    @staticmethod
    def _book_table(user, restaurant_name: str, date: str, time: str, guest_count: int, special_requests: str = "") -> dict:
        from restaurants.models import Restaurant
        from dining.models import DiningVenue, TableReservation
        import datetime
        
        restaurant = Restaurant.objects.filter(name__icontains=restaurant_name, is_active=True).first()
        if not restaurant:
            return {"success": False, "message": f"Could not find a restaurant named '{restaurant_name}'"}
            
        venue = DiningVenue.objects.filter(restaurant=restaurant, is_active=True).first()
        if not venue:
            return {"success": False, "message": f"'{restaurant.name}' does not offer table booking."}
            
        try:
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            parsed_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
        except ValueError:
            return {"success": False, "message": "Invalid date or time format. Please use YYYY-MM-DD and HH:MM:SS."}
            
        if not restaurant.is_open_at(parsed_time):
            return {"success": False, "message": f"'{restaurant.name}' is closed at the requested time. Operating hours: {restaurant.formatted_hours}."}
            
        res = TableReservation.objects.create(
            user=user,
            venue=venue,
            date=parsed_date,
            time=parsed_time,
            guest_count=guest_count,
            special_requests=special_requests,
            status=TableReservation.Status.CONFIRMED
        )
        return {"success": True, "message": f"Table booked successfully at {restaurant.name} for {guest_count} people on {date} at {time}!"}

    @staticmethod
    def _add_to_cart(user, restaurant_name: str, item_name: str, quantity: int) -> dict:
        from restaurants.models import Restaurant
        from menu.models import MenuItem
        from cart.models import Cart, CartItem
        
        restaurant = Restaurant.objects.filter(name__icontains=restaurant_name, is_active=True).first()
        if not restaurant:
            return {"success": False, "message": f"Could not find a restaurant named '{restaurant_name}'"}
            
        item = MenuItem.objects.filter(restaurant=restaurant, name__icontains=item_name, is_available=True).first()
        if not item:
            return {"success": False, "message": f"Could not find '{item_name}' on the menu at {restaurant.name}"}
            
        cart, _ = Cart.objects.get_or_create(user=user)
        
        first_item = cart.items.first()
        if first_item and first_item.menu_item.restaurant != restaurant:
            cart.items.all().delete()
            
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=item, defaults={"quantity": quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        return {"success": True, "message": f"Added {quantity}x {item.name} from {restaurant.name} to your cart!"}

    @staticmethod
    def _checkout_cart(user) -> dict:
        from cart.models import Cart
        from orders.models import Order, OrderItem
        
        cart = Cart.objects.filter(user=user).prefetch_related("items__menu_item__restaurant").first()
        if not cart or not cart.items.exists():
            return {"success": False, "message": "Your cart is empty!"}
            
        first_item = cart.items.first()
        restaurant = first_item.menu_item.restaurant
        
        total = sum(float(item.menu_item.effective_price) * item.quantity for item in cart.items.all())
        delivery_fee = 50.0
        tax = total * 0.05
        grand_total = total + delivery_fee + tax
        
        order = Order.objects.create(
            user=user,
            restaurant=restaurant,
            subtotal=total,
            delivery_fee=delivery_fee,
            tax=tax,
            grand_total=grand_total,
            status=Order.Status.CONFIRMED,
            payment_status=Order.PaymentStatus.PAID,
            payment_method=Order.PaymentMethod.COD,
            delivery_address="123 AI Boulevard, Tech City",
            delivery_city="Tech City",
            delivery_pincode="100001",
            estimated_delivery_time=30
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                name=item.menu_item.name,
                price=item.menu_item.effective_price,
                quantity=item.quantity
            )
            
        cart.items.all().delete()
        
        return {"success": True, "message": f"Order placed successfully! Order ID: {str(order.id)[:8].upper()}"}

    @staticmethod
    def run_agent(user, message: str, history: list, image_base64: str = None) -> dict:
        """
        Run the AI agent with function calling.
        Returns: { "reply": str, "action": str|None, "action_data": dict|None }
        """
        try:
            from django.conf import settings as django_settings
            import openai

            key = getattr(django_settings, 'GROQ_API_KEY', '')
            if not key:
                return {"reply": "AI Agent is not configured. Please add GROQ_API_KEY.", "action": None}

            import httpx
            client = openai.OpenAI(
                api_key=key,
                base_url=getattr(django_settings, 'GROQ_BASE_URL', 'https://api.groq.com/openai/v1'),
                http_client=httpx.Client(),
            )
            model = getattr(django_settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
            
            # ── Vision Pre-processing ─────────────────────────────────────
            vision_context = ""
            if image_base64:
                try:
                    vision_messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Identify the food, dish, or item in this image concisely. If it's a food, just name the food. Keep it under 10 words."},
                                {"type": "image_url", "image_url": {"url": image_base64}}
                            ]
                        }
                    ]
                    vision_res = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=vision_messages,
                        max_tokens=100,
                        temperature=0.2,
                    )
                    image_description = vision_res.choices[0].message.content.strip()
                    vision_context = f"\n[User attached an image containing: {image_description}]\n"
                except Exception as e:
                    logger.error("Vision API error: %s", e)
            # ──────────────────────────────────────────────────────────────

            # Build messages
            messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
            for h in (history or []):
                role = h.get("role", "user")
                if role in ("user", "assistant"):
                    messages.append({"role": role, "content": h.get("content", "")})
            
            # Combine vision context with user message
            final_user_message = message
            if vision_context:
                final_user_message = f"{vision_context}\nUser says: {message}" if message else vision_context.strip()
            elif not message:
                final_user_message = "Hello" # Fallback if empty

            messages.append({"role": "user", "content": final_user_message})

            # First call — may include tool use
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=AGENT_TOOLS,
                tool_choice="auto",
                parallel_tool_calls=False,
                max_tokens=500,
                temperature=0.4,
            )

            choice = response.choices[0]
            action_executed = None
            action_data = None

            # Handle tool calls
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                tool_calls = choice.message.tool_calls
                messages.append(choice.message)  # append assistant message with tool calls

                tool_results = []
                for tc in tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except Exception:
                        fn_args = {}

                    result = AIAgent.execute_tool(fn_name, fn_args, user)
                    action_executed = fn_name
                    action_data = result

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    })

                messages.extend(tool_results)

                # Second call — get final response with tool results
                response2 = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=400,
                    temperature=0.4,
                )
                final_reply = response2.choices[0].message.content

            else:
                final_reply = choice.message.content

            return {
                "reply": final_reply,
                "action": action_executed,
                "action_data": action_data,
            }

        except Exception as e:
            logger.error("AI Agent error: %s", e)
            return {"reply": "I'm having trouble right now. Please try again in a moment! 🙏", "action": None}
