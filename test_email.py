"""Test email configuration"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel_delivery.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=== Django Email Settings ===")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(EMPTY)'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

print("\n=== Sending Test Email ===")
try:
    result = send_mail(
        'Test Email from Django - April 4, 2026',
        'If you see this email, Django email configuration is working!',
        settings.DEFAULT_FROM_EMAIL,
        ['shahzaibsadiq256@gmail.com'],
        fail_silently=False
    )
    print(f'✓ SUCCESS! Email sent to shahzaibsadiq256@gmail.com')
    print(f'✓ Message count: {result}')
except Exception as e:
    print(f'✗ FAILED: {type(e).__name__}')
    print(f'✗ Error: {e}')
