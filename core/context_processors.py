from django.conf import settings


def site_settings(request):
    """
    Makes `site_settings` available to templates as `{{ site_settings.<field> }}`.
    """
    return {
        "site_settings": {
            "site_name": getattr(settings, "SITE_NAME", ""),
            "site_phone": getattr(settings, "SITE_PHONE", ""),
            "site_email": getattr(settings, "SITE_EMAIL", ""),
            "site_address": getattr(settings, "SITE_ADDRESS", ""),
            "service_area": getattr(settings, "SERVICE_AREA", ""),
        }
    }

