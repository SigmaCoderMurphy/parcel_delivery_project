"""
Django settings for parcel_delivery project.

Production (Namecheap cPanel + Passenger): set DEBUG=False, SECRET_KEY, ALLOWED_HOSTS,
CSRF_TRUSTED_ORIGINS, SQLITE_PATH (outside public_html), and BEHIND_TLS_PROXY=True when SSL
terminates at the host proxy.
"""

import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-local-dev-only-change-me")

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = [
    h.strip()
    for h in config(
        "ALLOWED_HOSTS",
        default="easternlogistics.app,www.easternlogistics.app,localhost,127.0.0.1",
    ).split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        "CSRF_TRUSTED_ORIGINS",
        default=(
            "https://easternlogistics.app,"
            "https://www.easternlogistics.app,"
            "http://localhost,"
            "http://127.0.0.1"
        ),
    ).split(",")
    if origin.strip()
]

# Brevo
BREVO_API_KEY = config("BREVO_API_KEY", default=None)
BREVO_SENDER_EMAIL = config("BREVO_SENDER_EMAIL", default="noreply@example.com")
BREVO_SENDER_NAME = config("BREVO_SENDER_NAME", default="Eastern Logistics")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "crispy_forms",
    "crispy_bootstrap5",
    # "import_export",  # optional; enable if openpyxl/Python versions match
    "django_recaptcha",
    "core",
    "leads",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if not DEBUG:
    MIDDLEWARE.insert(4, "core.middleware.HtmlMinifyMiddleware")

ROOT_URLCONF = "parcel_delivery.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                *(
                    ["django.template.context_processors.debug"]
                    if DEBUG
                    else []
                ),
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "parcel_delivery.wsgi.application"

# -----------------------------------------------------------------------------
# Database — SQLite only (store outside web root on shared hosting via SQLITE_PATH)
# -----------------------------------------------------------------------------
_sqlite_path = config("SQLITE_PATH", default="").strip()
if _sqlite_path:
    _db_path = Path(_sqlite_path).expanduser().resolve()
    _db_path.parent.mkdir(parents=True, exist_ok=True)
else:
    _db_path = (BASE_DIR / "db.sqlite3").resolve()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(_db_path),
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    WHITENOISE_KEEP_ONLY_HASHED_FILES = True
    WHITENOISE_MAX_AGE = 31536000

MEDIA_URL = "/media/"
_media_root = config("MEDIA_ROOT_PATH", default="").strip()
if _media_root:
    MEDIA_ROOT = Path(_media_root).expanduser().resolve()
else:
    MEDIA_ROOT = (BASE_DIR / "media").resolve()
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/dashboard/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.zoho.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER", default="")

SITE_NAME = "Eastern Logistics"
SITE_PHONE = "416-710-0361"
SITE_EMAIL = "support@easternlogistics.app"
SITE_ADDRESS = "828 Eastern Ave, Toronto, ON M4L 1A1, Canada"
SERVICE_AREA = "Greater Toronto Area (GTA)"
SITE_GOOGLE_BUSINESS_URL = "https://maps.app.goo.gl/gEr1qAS8g4DRXYkNA?g_st=aw"
SITE_URL = config("SITE_URL", default="https://easternlogistics.app")
STAFF_WHATSAPP_NUMBER = config("STAFF_WHATSAPP_NUMBER", default="")
ADMIN_URL = config("ADMIN_URL", default="admin/")

TWILIO_WEBHOOK_PUBLIC_URL = config("TWILIO_WEBHOOK_PUBLIC_URL", default="").strip()

GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY", default="")
MAP_BUSINESS_LAT = config("MAP_BUSINESS_LAT", default=43.661937, cast=float)
MAP_BUSINESS_LNG = config("MAP_BUSINESS_LNG", default=-79.3288, cast=float)
MAP_SERVICE_RADIUS_METERS = config("MAP_SERVICE_RADIUS_METERS", default=35000, cast=int)

RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY", default="")
RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY", default="")

# Passenger / cPanel: SSL often terminates at Apache; Django sees HTTP internally.
BEHIND_TLS_PROXY = config("BEHIND_TLS_PROXY", default=False, cast=bool)
if not BEHIND_TLS_PROXY and os.environ.get("PASSENGER_APP_ENV"):
    BEHIND_TLS_PROXY = True

# -----------------------------------------------------------------------------
# Production security (DEBUG=False)
# -----------------------------------------------------------------------------
if not DEBUG:
    if not SECRET_KEY or SECRET_KEY.startswith("django-insecure-local-dev-only-change-me"):
        raise ValueError("SECRET_KEY must be set to a strong random value when DEBUG=False")
    if ALLOWED_HOSTS == ["localhost", "127.0.0.1"]:
        raise ValueError("Set ALLOWED_HOSTS for production (e.g. easternlogistics.app,www.easternlogistics.app)")

    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    if BEHIND_TLS_PROXY:
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
        USE_X_FORWARDED_HOST = True
    else:
        _proxy_ssl = config("SECURE_PROXY_SSL_HEADER", default="").strip()
        if _proxy_ssl:
            _parts = _proxy_ssl.split(",", 1)
            if len(_parts) == 2:
                SECURE_PROXY_SSL_HEADER = (_parts[0].strip(), _parts[1].strip())
        USE_X_FORWARDED_HOST = config("USE_X_FORWARDED_HOST", default=False, cast=bool)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "parcel-delivery-cache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if not DEBUG else "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
