"""
CraveHub — Instamart Service Layer
"""

from __future__ import annotations
from django.core.cache import cache
from django.db.models import Q

from .models import InstamartCategory, InstamartStore, InstamartProduct
from .serializers import (
    InstamartCategorySerializer, InstamartStoreSerializer,
    InstamartProductSerializer, InstamartProductListSerializer,
)

CACHE_TTL = 60 * 5


class InstamartService:

    @staticmethod
    def get_home(city: str | None = None) -> dict:
        cache_key = f"cravehub:instamart:home:{city or 'all'}"
        cached    = cache.get(cache_key)
        if cached:
            return cached

        stores_qs = InstamartStore.objects.filter(
            is_active=True, is_deleted=False, is_open=True
        )
        if city:
            stores_qs = stores_qs.filter(city__icontains=city)

        categories = InstamartCategory.objects.filter(
            is_active=True
        ).order_by("display_order")[:50]

        featured_products = InstamartProduct.objects.filter(
            is_available=True, is_featured=True,
            store__is_active=True, store__is_deleted=False,
        ).select_related("store", "category").order_by("-id")[:100]

        all_products = InstamartProduct.objects.filter(
            is_available=True,
            store__is_active=True, store__is_deleted=False,
        ).select_related("category")

        data = {
            "stores":           InstamartStoreSerializer(stores_qs[:10], many=True).data,
            "categories":       InstamartCategorySerializer(categories, many=True).data,
            "featured_products":InstamartProductListSerializer(featured_products, many=True).data,
            "all_products":     InstamartProductListSerializer(all_products, many=True).data,
        }
        cache.set(cache_key, data, CACHE_TTL)
        return data

    @staticmethod
    def get_store_products(store_id: str, filters: dict, params) -> tuple:
        qs = InstamartProduct.objects.filter(
            store_id=store_id,
            store__is_active=True,
            store__is_deleted=False,
        ).select_related("category")

        if filters.get("category"):
            qs = qs.filter(category_id=filters["category"])
        if filters.get("available") is not None:
            qs = qs.filter(is_available=filters["available"])
        if filters.get("q"):
            qs = qs.filter(
                Q(name__icontains=filters["q"])
                | Q(brand__icontains=filters["q"])
                | Q(description__icontains=filters["q"])
            )

        qs    = qs.order_by("-is_featured", "name")
        total = qs.count()
        return InstamartProductListSerializer(
            qs[params.offset: params.offset + params.limit], many=True
        ).data, total

    @staticmethod
    def get_product(product_id: str) -> dict | None:
        try:
            p = InstamartProduct.objects.select_related("store", "category").get(pk=product_id)
            return InstamartProductSerializer(p).data
        except InstamartProduct.DoesNotExist:
            return None

    @staticmethod
    def get_user_orders(user) -> list[dict]:
        from .models import InstamartOrder
        from .serializers import InstamartOrderSerializer
        qs = InstamartOrder.objects.filter(user=user).select_related("store").prefetch_related("items")
        return InstamartOrderSerializer(qs, many=True).data

    @staticmethod
    def place_order(user, data: dict) -> dict:
        from .models import InstamartOrder, InstamartOrderItem, InstamartStore
        from .serializers import InstamartOrderSerializer
        
        # very basic mock-like placement
        store = InstamartStore.objects.filter(is_active=True).first()
        if not store:
            raise ValueError("No active Instamart store available.")
            
        if not store.is_currently_open:
            raise ValueError(f"'{store.name}' is currently closed. Operating hours: {store.formatted_hours}.")
        
        cart_total = data.get("cartTotal", 0)
        cart_subtotal = data.get("cartSubtotal", 0)
        
        order = InstamartOrder.objects.create(
            user=user,
            store=store,
            payment_method=data.get("payMode", "cod").lower(),
            subtotal=cart_subtotal,
            discount=data.get("discountAmt", 0),
            delivery_fee=data.get("deliveryFee", 0),
            tax=data.get("tax", 0),
            grand_total=cart_total,
            delivery_address=data.get("deliveryAddress", "Mock Address, Chennai"),
            is_gift=data.get("is_gift", False),
            recipient_name=data.get("recipient_name", ""),
            recipient_mobile=data.get("recipient_mobile", ""),
            recipient_email=data.get("recipient_email", ""),
            gift_message=data.get("gift_message", ""),
            delivery_schedule_type=data.get("delivery_schedule_type", "now"),
            scheduled_delivery_time=data.get("scheduled_delivery_time", None)
        )
        
        cart_items = data.get("items", [])
        for item in cart_items:
            product_id = str(item.get("id")).replace("promo-", "")
            try:
                p = InstamartProduct.objects.get(pk=product_id)
                InstamartOrderItem.objects.create(
                    order=order,
                    product=p,
                    name=item.get("name", p.name),
                    price_at_purchase=item.get("effective_price", p.price),
                    quantity=item.get("quantity", 1)
                )
            except InstamartProduct.DoesNotExist:
                continue
                
        return InstamartOrderSerializer(order).data
