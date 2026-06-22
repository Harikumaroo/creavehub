"""
CraveHub — Root URL Configuration (Complete — All Phases)
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth
    path("api/", include("accounts.urls")),

    # Phase 1
    path("api/v1/categories/",  include("categories.urls")),
    path("api/v1/banners/",     include("banners.urls")),
    path("api/v1/offers/",      include("offers.urls")),

    # Phase 2
    path("api/v1/restaurants/", include("restaurants.urls")),
    path("api/v1/",             include("menu.urls")),
    path("api/v1/cart/",        include("cart.urls")),

    # Phase 3
    path("api/v1/orders/",      include("orders.urls")),
    path("api/v1/payments/",    include("payments.urls")),
    path("api/v1/reviews/",     include("reviews.urls")),

    # Phase 4
    path("api/v1/dashboard/",     include("dashboard.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/search/",        include("search.urls")),
    path("api/v1/ai/",            include("ai_engine.urls")),
    path("api/v1/instamart/",     include("instamart.urls")),
    path("api/v1/dining/",        include("dining.urls")),
    path("api/v1/parties/",       include("parties.urls")),
    path("api/v1/gifts/",         include("gifts.urls")),
    path("api/v1/catering/",      include("catering.urls")),
    path("api/v1/tracking/",      include("tracking.urls")),
    path("api/v1/support/",       include("support.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
