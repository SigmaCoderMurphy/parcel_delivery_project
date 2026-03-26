"""
ASGI config for parcel_delivery project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel_delivery.settings')

application = get_asgi_application()