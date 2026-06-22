"""
CraveHub — Recommendation Engine
Rule-based fallback + optional Claude/GPT enhancement.
"""

from __future__ import annotations
import json
import logging
import time
from django.conf import settings

from restaurants.models import Restaurant
from menu.models import MenuItem

logger = logging.getLogger(__name__)


class RecommendationEngine:

    @staticmethod
    def get_recommendations(user, context: str = "home") -> dict:
        """
        Main entrypoint. Uses rule-based engine by default.
        If OPENAI_API_KEY or ANTHROPIC_API_KEY is set, enhances with LLM.
        """
        start = time.time()

        try:
            profile = user.preference_profile
        except Exception:
            profile = None

        # Rule-based recommendations
        result = RecommendationEngine._rule_based(user, profile, context)

        # Optionally enhance with an LLM when API keys are configured.
        try:
            groq_key = getattr(settings, "GROQ_API_KEY", "")
            openai_key = getattr(settings, "OPENAI_API_KEY", "")
            anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", "")
            if groq_key or openai_key or anthropic_key:
                enhanced = RecommendationEngine._enhance_with_llm(user, profile, context, result)
                if enhanced:
                    result = enhanced
        except Exception as exc:
            logger.warning("LLM enhancement skipped/failure: %s", exc)

        latency = int((time.time() - start) * 1000)
        RecommendationEngine._log(user, context, result, latency)
        return result

    @staticmethod
    def _enhance_with_llm(user, profile, context: str, base_result: dict) -> dict | None:
        """
        Call an LLM (OpenAI or Anthropic) to refine the rule-based recommendations.
        This is best-effort: any failure will return None and leave the base_result intact.
        """
        try:
            from . import prompts
            import datetime
            import json

            restaurants_json = json.dumps(base_result.get("restaurants", []))
            current_time = datetime.datetime.utcnow().isoformat()

            user_profile_vals = {
                "prefers_veg": getattr(profile, "prefers_veg", False) if profile else False,
                "favourite_cuisines": getattr(profile, "favourite_cuisines", []) if profile else [],
                "avg_order_value": getattr(profile, "avg_order_value", 0) if profile else 0,
                "total_orders": getattr(profile, "total_orders", 0) if profile else 0,
            }

            user_prompt = prompts.RECOMMENDATION_USER_TEMPLATE.format(
                prefers_veg=user_profile_vals["prefers_veg"],
                favourite_cuisines=", ".join(user_profile_vals["favourite_cuisines"]) if user_profile_vals["favourite_cuisines"] else "none",
                avg_order_value=user_profile_vals["avg_order_value"],
                total_orders=user_profile_vals["total_orders"],
                restaurants_json=restaurants_json,
                current_time=current_time,
                context=context,
            )

            # Try Groq first (OpenAI-compatible, ultra-fast), then OpenAI, then Anthropic.
            text = None
            if getattr(settings, "GROQ_API_KEY", ""):
                try:
                    import httpx
                    import openai
                    model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
                    base_url = getattr(settings, "GROQ_BASE_URL", "https://api.groq.com/openai/v1")
                    client = openai.OpenAI(
                        api_key=settings.GROQ_API_KEY,
                        base_url=base_url,
                        http_client=httpx.Client(),
                    )
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": prompts.RECOMMENDATION_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        max_tokens=512,
                        temperature=0.2,
                    )
                    text = resp.choices[0].message.content
                except Exception as e:
                    logger.warning("Groq call failed: %s", e)
                    text = None

            if not text and getattr(settings, "OPENAI_API_KEY", ""):
                try:
                    import openai
                    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

                    if hasattr(openai, "OpenAI"):
                        import httpx
                        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, http_client=httpx.Client())
                        resp = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": prompts.RECOMMENDATION_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                            max_tokens=512,
                            temperature=0.2,
                        )
                        try:
                            text = resp.choices[0].message.content
                        except Exception:
                            try:
                                text = resp["choices"][0]["message"]["content"]
                            except Exception:
                                text = None
                    else:
                        openai.api_key = settings.OPENAI_API_KEY
                        resp = openai.ChatCompletion.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": prompts.RECOMMENDATION_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                            max_tokens=512,
                            temperature=0.2,
                        )
                        text = resp["choices"][0]["message"]["content"]
                except Exception as e:
                    logger.warning("OpenAI call failed: %s", e)
                    text = None

            if not text and getattr(settings, "ANTHROPIC_API_KEY", ""):
                try:
                    import anthropic
                    client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
                    prompt = prompts.RECOMMENDATION_SYSTEM_PROMPT + "\n" + user_prompt
                    resp = client.complete(prompt=prompt, model=getattr(settings, "ANTHROPIC_MODEL", "claude-2.1"), max_tokens=400)
                    text = resp.get("completion") or resp.get("text")
                except Exception as e:
                    logger.warning("Anthropic call failed: %s", e)
                    text = None

            if not text:
                return None

            parsed = json.loads(text)

            # Helper to pick items from serialized lists by id
            def pick_by_ids(serialized_objs, ids):
                idset = set(str(i) for i in ids)
                return [o for o in serialized_objs if str(o.get("id")) in idset]

            restaurants = pick_by_ids(base_result.get("restaurants", []), parsed.get("restaurant_ids", []))
            menu_items = pick_by_ids(base_result.get("menu_items", []), parsed.get("item_ids", []))

            return {
                "context": context,
                "model_used": "llm_enhanced",
                "restaurants": restaurants,
                "menu_items": menu_items,
                "reasoning": parsed.get("reasoning", ""),
            }
        except Exception as exc:
            logger.warning("LLM enhancement failed: %s", exc)
            return None

    @staticmethod
    def _rule_based(user, profile, context: str) -> dict:
        """
        Fast rule-based fallback:
        - Featured + open restaurants
        - Top-rated menu items
        - Veg filter if user prefers veg
        """
        rest_qs = (
            Restaurant.objects
            .filter(is_active=True, is_deleted=False, is_open=True)
            .select_related("address")
            .order_by("-is_featured", "-rating")
        )

        if profile and profile.prefers_veg:
            rest_qs = rest_qs.filter(is_pure_veg=True)

        restaurants = list(rest_qs[:8])

        item_qs = (
            MenuItem.objects
            .filter(is_available=True, restaurant__is_active=True, restaurant__is_deleted=False)
            .select_related("restaurant", "category")
            .order_by("-created_at")
        )

        if profile and profile.prefers_veg:
            item_qs = item_qs.filter(is_veg=True)

        if profile and profile.favourite_categories:
            item_qs = item_qs.filter(category_id__in=profile.favourite_categories)

        items = list(item_qs[:10])

        from restaurants.serializers import RestaurantListSerializer
        from menu.serializers import MenuItemSerializer

        return {
            "context":     context,
            "model_used":  "rule_based",
            "restaurants": RestaurantListSerializer(restaurants, many=True).data,
            "menu_items":  MenuItemSerializer(items, many=True).data,
        }

    @staticmethod
    def _log(user, context: str, result: dict, latency_ms: int) -> None:
        from .models import AIRecommendationLog
        try:
            AIRecommendationLog.objects.create(
                user=user if user.is_authenticated else None,
                context=context,
                model_used=result.get("model_used", "rule_based"),
                recommended_restaurant_ids=[
                    str(r["id"]) for r in result.get("restaurants", [])
                ],
                recommended_item_ids=[
                    str(i["id"]) for i in result.get("menu_items", [])
                ],
                latency_ms=latency_ms,
            )
        except Exception as exc:
            logger.warning("AI log failed: %s", exc)

    @staticmethod
    def update_preference_profile(user, order) -> None:
        """
        Called after order delivery to update user's preference profile.
        """
        from .models import UserPreferenceProfile
        profile, _ = UserPreferenceProfile.objects.get_or_create(user=user)

        # Update order stats
        profile.total_orders += 1

        # Running average order value
        prev_avg   = float(profile.avg_order_value)
        new_val    = float(order.grand_total)
        profile.avg_order_value = (
            (prev_avg * (profile.total_orders - 1) + new_val) / profile.total_orders
        )

        # Update category preferences from order items
        cat_ids = list(
            order.items
            .filter(menu_item__category__isnull=False)
            .values_list("menu_item__category_id", flat=True)
            .distinct()
        )
        existing = set(str(c) for c in profile.favourite_categories)
        for cid in cat_ids:
            existing.add(str(cid))
        profile.favourite_categories = list(existing)[:10]  # keep top 10

        profile.save()
