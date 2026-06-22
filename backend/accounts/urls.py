from django.urls import path
from .views import (
    # Registration
    RegisterMobileView, RegisterVerifyOTPView, RegisterCompleteView,
    # Login
    LoginMobileView, LoginVerifyOTPView,
    # Logout
    LogoutView,
    # Devices
    DeviceListView, DeviceLogoutView, DeviceLogoutAllView,
    # Profile
    ProfileView, ProfileUpdateView,
    # Token
    CraveHubTokenRefreshView,
    # Settings & Address
    UserAddressViewSet, UserSettingsView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'addresses', UserAddressViewSet, basename='address')


urlpatterns = [
    # ── Registration ─────────────────────────────────────────
    path("register/mobile/",      RegisterMobileView.as_view(),      name="register-mobile"),
    path("register/verify-otp/",  RegisterVerifyOTPView.as_view(),   name="register-verify-otp"),
    path("register/complete/",    RegisterCompleteView.as_view(),     name="register-complete"),

    # ── Login ─────────────────────────────────────────────────
    path("login/mobile/",         LoginMobileView.as_view(),         name="login-mobile"),
    path("login/verify-otp/",     LoginVerifyOTPView.as_view(),      name="login-verify-otp"),

    # ── Logout ────────────────────────────────────────────────
    path("logout/",               LogoutView.as_view(),              name="logout"),

    # ── Device Management ─────────────────────────────────────
    path("devices/",              DeviceListView.as_view(),          name="device-list"),
    path("devices/logout/",       DeviceLogoutView.as_view(),        name="device-logout"),
    path("devices/logout-all/",   DeviceLogoutAllView.as_view(),     name="device-logout-all"),

    # ── Profile ───────────────────────────────────────────────
    path("profile/",              ProfileView.as_view(),             name="profile"),
    path("profile/update/",       ProfileUpdateView.as_view(),       name="profile-update"),

    # ── Token ─────────────────────────────────────────────────
    path("token/refresh/",        CraveHubTokenRefreshView.as_view(), name="token-refresh"),

    # ── Settings ──────────────────────────────────────────────
    path("settings/",             UserSettingsView.as_view(),        name="settings"),
]

urlpatterns += router.urls