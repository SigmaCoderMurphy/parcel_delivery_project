"""
One-time startup tasks for WSGI/ASGI workers (after Django is fully initialized).
"""
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)


def sync_site_domain():
    """Align django.contrib.sites.Site with SITE_URL / PASSWORD_RESET_DOMAIN."""
    try:
        from django.contrib.sites.models import Site
    except Exception:  # pragma: no cover
        return

    domain = (getattr(settings, "PASSWORD_RESET_DOMAIN", None) or "").strip()
    site_url = (getattr(settings, "SITE_URL", None) or "").strip()
    if not domain and site_url:
        try:
            domain = urlparse(site_url).netloc or ""
        except Exception:
            domain = ""
    domain = domain.strip().lower()
    if not domain:
        return

    site_id = getattr(settings, "SITE_ID", 1)
    name = (getattr(settings, "SITE_NAME", None) or "Eastern Logistics")[:50]

    try:
        with transaction.atomic():
            clash_qs = Site.objects.select_for_update().filter(domain=domain).exclude(pk=site_id)
            for other in clash_qs:
                other.domain = f"legacy-site-{other.pk}.invalid"
                other.save(update_fields=["domain"])
            site = Site.objects.select_for_update().filter(pk=site_id).first()
            if site is None:
                Site.objects.create(pk=site_id, domain=domain, name=name)
            else:
                site.domain = domain
                site.name = name
                site.save(update_fields=["domain", "name"])
    except (OperationalError, ProgrammingError) as exc:
        logger.warning("django.contrib.sites sync skipped (database unavailable): %s", exc)
    except IntegrityError as exc:
        logger.warning("django.contrib.sites sync skipped (integrity): %s", exc)


def run_wsgi_startup():
    """Called from WSGI/ASGI after the Django application object is created."""
    sync_site_domain()
