import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parcel_delivery.settings")

app = Celery("parcel_delivery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
