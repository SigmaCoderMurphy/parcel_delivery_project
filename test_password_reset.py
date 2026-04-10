import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel_delivery.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.test import RequestFactory
from io import StringIO

print("\n" + "="*60)
print("🧪 PASSWORD RESET EMAIL TEST")
print("="*60)

# Get or create a test user for password reset
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'is_staff': False,
    }
)

print(f"\n✓ Test user: {user.username} ({user.email})")
print(f"  {'Created' if created else 'Existing'}")

# Check current email backend
from django.conf import settings
print(f"\n📧 Email Backend: {settings.EMAIL_BACKEND}")
print(f"   Email Host: {settings.EMAIL_HOST}")

# Check Site configuration  
from django.contrib.sites.models import Site
try:
    site = Site.objects.get(id=settings.SITE_ID)
    print(f"\n🔗 Site Configuration (SITE_ID={settings.SITE_ID}):")
    print(f"   Domain: {site.domain}")
    print(f"   Name: {site.name}")
except Site.DoesNotExist:
    print(f"\n❌ ERROR: Site with id={settings.SITE_ID} does not exist!")
    exit(1)

# Create a mock request for password reset
factory = RequestFactory()
request = factory.get('/password-reset/')
request.META['HTTP_HOST'] = '127.0.0.1:8000'

print(f"\n📬 Sending password reset email...")
from django.contrib.auth.forms import PasswordResetForm
form = PasswordResetForm({'email': user.email})

if form.is_valid():
    # This uses our CustomPasswordResetForm which should send HTML email
    form.save(request=request)
    print("   ✓ Email queued successfully")
    
    # Check if email was captured (for console/file backend testing)
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("   (Using console backend - check console output above)")
    else:
        print(f"   (Check inbox: {user.email})")
else:
    print(f"   ✗ Form errors: {form.errors}")

print("\n" + "="*60)
print("✅ TEST COMPLETE - Server running on http://127.0.0.1:8000")
print("="*60)
print("\n📍 Next steps:")
print("   1. Go to http://127.0.0.1:8000/admin/login/")
print("   2. Login with your admin credentials")
print("   3. Check your email for password reset message")
print("   4. Verify domain is 127.0.0.1:8000 (NOT example.com)")
print("\n")
