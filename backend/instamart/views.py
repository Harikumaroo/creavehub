"""
CraveHub — Instamart Views
"""

from rest_framework.request import Request
from rest_framework.views import APIView

from core.exceptions import NotFoundError
from core.helpers import error_response, paginated_response, success_response
from core.helpers.pagination import PaginationParams
from core.permissions import AllowAny

from .services import InstamartService


class InstamartHomeView(APIView):
    """
    GET /api/v1/instamart/
    Returns stores, categories, featured products.
    Optional: ?city=Chennai
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        city = request.query_params.get("city", "").strip() or None
        data = InstamartService.get_home(city=city)
        return success_response(data=data, message="Instamart home loaded successfully")


class StoreProductListView(APIView):
    """
    GET /api/v1/instamart/stores/<uuid>/products/
    Query params: category=<uuid>, available=true, q=milk, page=1
    """
    permission_classes = [AllowAny]

    def get(self, request: Request, store_id):
        params  = PaginationParams.from_request(request)
        filters = {
            "category":  request.query_params.get("category"),
            "available": True,
            "q":         request.query_params.get("q", "").strip() or None,
        }
        data, total = InstamartService.get_store_products(
            store_id=str(store_id), filters=filters, params=params
        )
        return paginated_response(
            data=data, page=params.page,
            page_size=params.page_size, total_count=total,
            message="Products fetched successfully",
        )


class InstamartProductDetailView(APIView):
    """
    GET /api/v1/instamart/products/<uuid>/
    """
    permission_classes = [AllowAny]

    def get(self, request: Request, pk):
        data = InstamartService.get_product(product_id=str(pk))
        if not data:
            return error_response("Product not found", status_code=404)
        return success_response(data=data, message="Product fetched successfully")

from rest_framework.permissions import IsAuthenticated

class InstamartOrderListView(APIView):
    """
    GET /api/v1/instamart/orders/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        data = InstamartService.get_user_orders(request.user)
        return success_response(data=data, message="Orders fetched successfully")


class InstamartOrderPlaceView(APIView):
    """
    POST /api/v1/instamart/orders/place/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        try:
            data = InstamartService.place_order(request.user, request.data)
            return success_response(data=data, message="Order placed successfully")
        except ValueError as e:
            return error_response(str(e), status_code=400)
        except Exception as e:
            return error_response("Failed to place order.", status_code=500)

from .models import InstamartCart, InstamartCartItem, InstamartProduct
from .serializers import InstamartCartSerializer

class InstamartAddToCartView(APIView):
    """
    POST /api/v1/instamart/cart/add/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        from django.core.exceptions import ValidationError
        try:
            product = InstamartProduct.objects.select_related("store").get(pk=product_id, is_available=True)
        except (InstamartProduct.DoesNotExist, ValidationError):
            return error_response("Product not found or unavailable.", status_code=404)

        if not product.store.is_currently_open:
            return error_response(f"'{product.store.name}' is currently closed. Cannot add items to cart.", status_code=400)

        cart, _ = InstamartCart.objects.get_or_create(user=request.user)
        
        cart_item, created = InstamartCartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return success_response(data={"cart_id": cart.id}, message="Item added to Instamart cart")


from .serializers import InstamartProductListSerializer
from django.db.models import Q

class InstamartProductSearchView(APIView):
    """
    GET /api/v1/instamart/search/?q=xyz
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return success_response(data=[], message="No query provided")

        qs = InstamartProduct.objects.filter(
            is_available=True,
            store__is_active=True,
            store__is_deleted=False
        ).select_related("category").filter(
            Q(name__icontains=q) |
            Q(brand__icontains=q) |
            Q(description__icontains=q)
        ).order_by("-is_featured", "name")[:20]

        data = InstamartProductListSerializer(qs, many=True).data
        return success_response(data=data, message="Search results fetched successfully")


class InstamartCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        cart, _ = InstamartCart.objects.get_or_create(user=request.user)
        items = InstamartCartItem.objects.filter(cart=cart).select_related("product")
        
        items_data = []
        subtotal = 0
        for item in items:
            price = item.product.effective_price
            items_data.append({
                "id": str(item.id),
                "product_id": str(item.product.id),
                "name": item.product.name,
                "brand": item.product.brand,
                "image": item.product.image,
                "price": float(price),
                "quantity": item.quantity,
                "line_total": float(price * item.quantity)
            })
            subtotal += price * item.quantity

        delivery_fee = 40.00 if subtotal > 0 else 0
        tax = float(subtotal) * 0.05
        grand_total = float(subtotal) + delivery_fee + tax

        return success_response(data={
            "id": str(cart.id),
            "items": items_data,
            "item_count": sum(i["quantity"] for i in items_data),
            "subtotal": float(subtotal),
            "delivery_fee": delivery_fee,
            "tax": tax,
            "grand_total": grand_total
        }, message="Cart fetched successfully")

class InstamartCartItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, pk):
        try:
            cart_item = InstamartCartItem.objects.get(pk=pk, cart__user=request.user)
            quantity = int(request.data.get("quantity", 1))
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return success_response(message="Cart item updated")
        except InstamartCartItem.DoesNotExist:
            return error_response("Item not found", status_code=404)

class InstamartCartItemRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, pk):
        try:
            cart_item = InstamartCartItem.objects.get(pk=pk, cart__user=request.user)
            cart_item.delete()
            return success_response(message="Cart item removed")
        except InstamartCartItem.DoesNotExist:
            return error_response("Item not found", status_code=404)

class InstamartCartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request):
        InstamartCartItem.objects.filter(cart__user=request.user).delete()
        return success_response(message="Cart cleared")