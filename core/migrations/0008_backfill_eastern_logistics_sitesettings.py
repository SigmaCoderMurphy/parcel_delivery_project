# Data migration: align existing SiteSettings row(s) with Eastern Logistics contact info.

from django.db import migrations

MAPS_URL = "https://maps.app.goo.gl/gEr1qAS8g4DRXYkNA?g_st=aw"


def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    for s in SiteSettings.objects.all():
        s.site_name = "Eastern Logistics"
        s.site_email = "shahzaibsadiq256@gmail.com"
        s.site_phone = "416-710-0361"
        if not (s.google_business_url or "").strip():
            s.google_business_url = MAPS_URL
        s.save()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_eastern_logistics_contact_defaults"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
