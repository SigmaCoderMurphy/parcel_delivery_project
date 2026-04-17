import logging
import sys

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core Website Management"

    def ready(self):
        if self._should_skip_startup_hooks():
            return
        self._warn_if_email_misconfigured()

    @staticmethod
    def _should_skip_startup_hooks():
        skip = {"migrate", "makemigrations"}
        return bool(skip.intersection(sys.argv[1:]))

    def _warn_if_email_misconfigured(self):
        if getattr(settings, "DEBUG", True):
            return
        backend = getattr(settings, "EMAIL_BACKEND", "") or ""
        if "locmem" in backend or "console" in backend or "dummy" in backend:
            logger.warning(
                "EMAIL_BACKEND is %s while DEBUG=False; outbound mail may not reach recipients.",
                backend,
            )
        if not (getattr(settings, "EMAIL_HOST_USER", "") or "").strip():
            logger.warning(
                "EMAIL_HOST_USER is empty while DEBUG=False; set SMTP credentials in the environment.",
            )
