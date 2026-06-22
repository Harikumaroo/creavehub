import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        'Test Subject',
        'Test Message.',
        os.environ.get('DEFAULT_FROM_EMAIL', 'cravehubai@gmail.com'),
        ['cravehubai@gmail.com'],
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
