from django.test import TestCase
from rest_framework.test import APIClient

from .models import User
from .services import TokenService, DeviceSessionService


class LogoutRevocationTest(TestCase):
    """Ensure logout blacklists the refresh token and access token is rejected."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            mobile_number='+911234567890', full_name='Test User', is_verified=True
        )

        tokens = TokenService.generate_tokens(self.user)
        self.access = tokens['access_token']
        self.refresh = tokens['refresh_token']
        self.jti = tokens['jti']

        # create a device session linked to the refresh token jti
        DeviceSessionService.create_session(
            user=self.user,
            device_id='test-device',
            device_type='web',
            device_name='pytest',
            ip_address='127.0.0.1',
            user_agent='test-agent',
            refresh_token_id=self.jti,
        )

    def test_logout_revokes_access(self):
        # Pre-check: protected endpoint should be accessible
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        pre = self.client.get('/api/v1/categories/')
        self.assertEqual(pre.status_code, 200)

        # Logout using the refresh token
        resp = self.client.post('/api/logout/', {'refresh_token': self.refresh}, format='json')
        self.assertEqual(resp.status_code, 200)

        # After logout the same access token must be rejected
        post = self.client.get('/api/v1/categories/')
        self.assertEqual(post.status_code, 401)
        # Message should indicate blacklist (string-match defensive)
        self.assertTrue('blacklist' in str(post.data).lower() or 'token is blacklisted' in str(post.data).lower())
