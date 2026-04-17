"""
WSGI config for parcel_delivery project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel_delivery.settings')
application = get_wsgi_application()

try:
    from core.bootstrap import run_wsgi_startup

    run_wsgi_startup()
except Exception:  # pragma: no cover — never break WSGI import
    pass