from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class RevocableJWTAuthentication(JWTAuthentication):
    """Extends JWTAuthentication to reject tokens that have been blacklisted.

    This implementation expects access tokens to carry the same JTI as the
    corresponding refresh token (we set this when issuing tokens). On logout
    the refresh token's OutstandingToken is blacklisted — checking the same
    JTI allows immediate revocation of access tokens.
    """

    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get("jti")
        if not jti:
            return token

        try:
            outstanding = OutstandingToken.objects.get(jti=jti)
        except OutstandingToken.DoesNotExist:
            raise AuthenticationFailed("Token not recognized")

        if BlacklistedToken.objects.filter(token=outstanding).exists():
            raise AuthenticationFailed("Token is blacklisted")

        return token
