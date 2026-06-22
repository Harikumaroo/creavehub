"""
CraveHub Authentication Views
All views are class-based using APIView.
Thin views — all logic delegated to service layer.
"""
from rest_framework          import status
from rest_framework.response import Response
from rest_framework.views    import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, viewsets


from .serializers import (
    RegisterMobileSerializer, RegisterVerifyOTPSerializer, RegisterCompleteSerializer,
    LoginMobileSerializer, LoginVerifyOTPSerializer,
    LogoutSerializer, DeviceLogoutSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer,
    DeviceSessionSerializer, UserAddressSerializer, UserSettingsSerializer
)
from .models import UserAddress, UserSettings
from .services import (
    RegistrationService, LoginService,
    TokenService, DeviceSessionService,
)
from .utils import (
    success_response, error_response,
    get_client_ip, get_user_agent, get_device_type,
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _device_context(request, data: dict) -> dict:
    """Extract device metadata from request."""
    ua = get_user_agent(request)
    return {
        "device_id":   data.get("device_id", ""),
        "device_type": data.get("device_type") or get_device_type(ua),
        "device_name": data.get("device_name", ""),
        "ip_address":  get_client_ip(request),
        "user_agent":  ua,
    }


def ok(message, data=None, http=status.HTTP_200_OK):
    return Response(success_response(message, data), status=http)


def err(message, errors=None, http=status.HTTP_400_BAD_REQUEST):
    return Response(error_response(message, errors), status=http)


# ═══════════════════════════════════════════════════════════════
# REGISTRATION VIEWS
# ═══════════════════════════════════════════════════════════════

class RegisterMobileView(APIView):
    """
    POST /api/register/mobile/
    Step 1 of registration: send OTP to new mobile number.
    """
    permission_classes = []
 
    def post(self, request):
        serializer = RegisterMobileSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)
 
        mobile = serializer.validated_data["mobile_number"]
        success, message, data = RegistrationService.initiate(mobile)
 
        if not success:
            return err(message, http=status.HTTP_409_CONFLICT)
        return ok(message, data, http=status.HTTP_200_OK)
 
 
class RegisterVerifyOTPView(APIView):
    """
    POST /api/register/verify-otp/
    Step 2: verify registration OTP.
    """
    permission_classes = []
 
    def post(self, request):
        serializer = RegisterVerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)
 
        vd      = serializer.validated_data
        success, message, data = RegistrationService.verify_otp(
            vd["mobile_number"], vd["otp"]
        )
 
        if not success:
            return err(message)
        return ok(message, data)
 
 
class RegisterCompleteView(APIView):
    """
    POST /api/register/complete/
    Step 3: create account, return tokens + device session.
    """
    permission_classes = []
 
    def post(self, request):
        serializer = RegisterCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)
 
        vd     = serializer.validated_data
        device = _device_context(request, vd)
 
        success, message, data = RegistrationService.complete(
            mobile_number=vd["mobile_number"],
            full_name=vd["full_name"],
            email=vd.get("email", ""),
            **device,
        )
 
        if not success:
            return err(message)
        return ok(message, data, http=status.HTTP_201_CREATED)
 



# ═══════════════════════════════════════════════════════════════
# LOGIN VIEWS
# ═══════════════════════════════════════════════════════════════

class LoginMobileView(APIView):
    """
    POST /api/login/mobile/
    Step 1: send OTP to registered mobile number.
    """
    permission_classes = []

    def post(self, request):
        serializer = LoginMobileSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)

        mobile = serializer.validated_data["mobile_number"]
        success, message, data = LoginService.initiate(mobile)

        if not success:
            return err(message, http=status.HTTP_404_NOT_FOUND)
        return ok(message, data)


class LoginVerifyOTPView(APIView):
    """
    POST /api/login/verify-otp/
    Step 2: verify OTP → create device session → return tokens.
    Previous device sessions are NEVER touched.
    """
    permission_classes = []

    def post(self, request):
        serializer = LoginVerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)

        vd     = serializer.validated_data
        device = _device_context(request, vd)

        success, message, data = LoginService.verify_otp(
            mobile_number=vd["mobile_number"],
            plain_otp=vd["otp"],
            **device,
        )

        if not success:
            return err(message)
        return ok(message, data)


# ═══════════════════════════════════════════════════════════════
# LOGOUT VIEWS
# ═══════════════════════════════════════════════════════════════

class LogoutView(APIView):
    """
    POST /api/logout/
    Blacklist current refresh token + deactivate its device session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)

        refresh_token = serializer.validated_data["refresh_token"]

        try:
            token = RefreshToken(refresh_token)
            jti   = token["jti"]
        except Exception:
            return err("Invalid refresh token.")

        # Deactivate device session
        DeviceSession_qs = request.user.device_sessions.filter(
            refresh_token_id=jti, is_active=True
        )
        for session in DeviceSession_qs:
            session.mark_inactive(reason="user_logout")

        TokenService.blacklist_token(refresh_token)
        return ok("Logged out successfully.")


# ═══════════════════════════════════════════════════════════════
# DEVICE MANAGEMENT VIEWS
# ═══════════════════════════════════════════════════════════════

class DeviceListView(APIView):
    """
    GET /api/devices/
    List all active device sessions for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = DeviceSessionService.get_active_sessions(request.user)
        data     = DeviceSessionSerializer(
            sessions, many=True, context={"request": request}
        ).data
        return ok("Active device sessions retrieved.", {
            "sessions":     data,
            "total_active": len(data),
        })


class DeviceLogoutView(APIView):
    """
    POST /api/devices/logout/
    Revoke a specific device session by session_id.
    Body: { "session_id": "<uuid>" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceLogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)

        session_id = str(serializer.validated_data["session_id"])
        success, message = DeviceSessionService.logout_device(request.user, session_id)

        if not success:
            return err(message, http=status.HTTP_404_NOT_FOUND)
        return ok(message)


class DeviceLogoutAllView(APIView):
    """
    POST /api/devices/logout-all/
    Revoke ALL active device sessions for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        success, message = DeviceSessionService.logout_all_devices(request.user)
        return ok(message)


# ═══════════════════════════════════════════════════════════════
# PROFILE VIEWS
# ═══════════════════════════════════════════════════════════════

class ProfileView(APIView):
    """
    GET /api/profile/
    Return authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return ok("Profile retrieved successfully.", serializer.data)


class ProfileUpdateView(APIView):
    """
    PUT /api/profile/update/
    Update full_name and/or email.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return err("Validation failed.", serializer.errors)

        serializer.save()
        return ok("Profile updated successfully.", UserProfileSerializer(request.user, context={'request': request}).data)


# ═══════════════════════════════════════════════════════════════
# TOKEN REFRESH VIEW (extended to touch device session)
# ═══════════════════════════════════════════════════════════════

class CraveHubTokenRefreshView(TokenRefreshView):
    """
    POST /api/token/refresh/
    Standard JWT refresh + updates device session last_active.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                old_refresh = request.data.get("refresh", "")
                token = RefreshToken(old_refresh)
                DeviceSessionService.update_last_active(str(token["jti"]))
            except Exception:
                pass
        return response


# ═══════════════════════════════════════════════════════════════
# ADDRESS & SETTINGS VIEWS
# ═══════════════════════════════════════════════════════════════

class UserAddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for User Addresses.
    """
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSettingsView(generics.RetrieveUpdateAPIView):
    """
    GET / PUT for User Settings.
    """
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, created = UserSettings.objects.get_or_create(user=self.request.user)
        return obj