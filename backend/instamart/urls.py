from django.urls import path
from .views import (
    InstamartHomeView, StoreProductListView, InstamartProductDetailView,
    InstamartOrderListView, InstamartOrderPlaceView,
    InstamartAddToCartView, InstamartProductSearchView,
    InstamartCartView, InstamartCartItemUpdateView,
    InstamartCartItemRemoveView, InstamartCartClearView
)

app_name = "instamart"

urlpatterns = [
    path("",                                  InstamartHomeView.as_view(),        name="home"),
    path("stores/<uuid:store_id>/products/",  StoreProductListView.as_view(),     name="store-products"),
    path("products/<uuid:pk>/",               InstamartProductDetailView.as_view(),name="product-detail"),
    path("orders/",                           InstamartOrderListView.as_view(),   name="order-list"),
    path("orders/place/",                     InstamartOrderPlaceView.as_view(),  name="order-place"),
    path("cart/",                             InstamartCartView.as_view(),        name="cart-get"),
    path("cart/add/",                         InstamartAddToCartView.as_view(),   name="cart-add"),
    path("cart/item/<uuid:pk>/",              InstamartCartItemUpdateView.as_view(),name="cart-item-update"),
    path("cart/item/<uuid:pk>/delete/",       InstamartCartItemRemoveView.as_view(),name="cart-item-delete"),
    path("cart/clear/",                       InstamartCartClearView.as_view(),   name="cart-clear"),
    path("search/",                           InstamartProductSearchView.as_view(),name="search"),
]
