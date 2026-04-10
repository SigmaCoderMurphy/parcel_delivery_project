import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel_delivery.settings')
django.setup()

from django.contrib.sites.models import Site

# First, let's check what sites exist
print("\n📋 Current sites in database:")
for site in Site.objects.all():
    print(f"   ID: {site.id}, Domain: {site.domain}, Name: {site.name}")

# Delete all existing sites
print("\n🗑️  Clearing old sites...")
Site.objects.all().delete()

# Create the correct default site with id=1
print("\n✨ Creating new default site...")
site = Site.objects.create(
    id=1,
    domain='127.0.0.1:8000',
    name='Eastern Logistics (Local)'
)

print(f"\n✅ Site created successfully!")
print(f"   ID: {site.id}")
print(f"   Domain: {site.domain}")
print(f"   Name: {site.name}")

# Verify it exists
print("\n📋 Sites in database now:")
for s in Site.objects.all():
    print(f"   ID: {s.id}, Domain: {s.domain}, Name: {s.name}")
print()
