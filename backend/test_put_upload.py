import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from django.test import Client
from accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken

# Create or get user
user, _ = User.objects.get_or_create(mobile_number="9999999999", defaults={"full_name": "Test"})
refresh = RefreshToken.for_user(user)
access = str(refresh.access_token)

client = Client()

# Create a dummy image
img = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
f = SimpleUploadedFile("avatar.gif", img, content_type="image/gif")

res = client.put(
    "/api/profile/update/",
    data={"avatar": f},
    HTTP_AUTHORIZATION=f"Bearer {access}",
)

print("Status:", res.status_code)
print("Response:", res.json())
