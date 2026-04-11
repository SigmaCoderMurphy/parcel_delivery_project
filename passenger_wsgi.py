"""
Phusion Passenger entrypoint for Namecheap cPanel (Python App).

In cPanel → Setup Python App, set:
  Application root: folder that contains this file and manage.py
  Application startup file: passenger_wsgi.py
  Application URL: your domain or subdirectory

Environment variables (including DJANGO_SETTINGS_MODULE) are usually injected by the
panel; this file sets a safe default.
"""
import os
import sys

# Project root = directory containing this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parcel_delivery.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
