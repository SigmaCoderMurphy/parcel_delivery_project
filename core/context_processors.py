import json

from django.conf import settings as django_settings

from .models import SiteSettings


def site_settings(request):
    """
    Makes `site_settings` available to templates as `{{ site_settings.<field> }}`.
    `google_business_url_resolved` falls back to SITE_GOOGLE_BUSINESS_URL when DB field is empty.
    """
    fallback_maps = getattr(django_settings, "SITE_GOOGLE_BUSINESS_URL", "") or ""
    try:
        settings_obj = SiteSettings.objects.first()
        if settings_obj:
            resolved = (settings_obj.google_business_url or "").strip() or fallback_maps
            ld = {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": settings_obj.site_name,
                "telephone": settings_obj.site_phone,
                "email": settings_obj.site_email,
                "url": getattr(django_settings, "SITE_URL", "").rstrip("/") or None,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": settings_obj.site_address.replace("\n", " ").strip()[:500],
                },
                "areaServed": settings_obj.service_area,
            }
            if resolved:
                ld["sameAs"] = [resolved]
            return {
                "site_settings": settings_obj,
                "google_business_url_resolved": resolved,
                "local_business_json_ld": json.dumps(ld, ensure_ascii=False),
            }
        ld = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": django_settings.SITE_NAME,
            "telephone": django_settings.SITE_PHONE,
            "email": django_settings.SITE_EMAIL,
            "url": getattr(django_settings, "SITE_URL", "").rstrip("/") or None,
        }
        return {
            "site_settings": None,
            "google_business_url_resolved": fallback_maps,
            "local_business_json_ld": json.dumps(ld, ensure_ascii=False),
        }
    except Exception:
        ld = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": getattr(django_settings, "SITE_NAME", "Business"),
        }
        return {
            "site_settings": None,
            "google_business_url_resolved": fallback_maps,
            "local_business_json_ld": json.dumps(ld, ensure_ascii=False),
        }
