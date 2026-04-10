# SEO, performance, and production audit — Eastern Logistics

This document is a practical checklist for a Django parcel-delivery site. Several items are **already implemented** in code (see repo); the rest is your ongoing work.

---

## What we fixed or added in the codebase

| Area | Change |
|------|--------|
| **Dashboard vs Leads** | Same definitions: **New** = `status=new`, **Qualified** = `status=qualified`, **Won** = `status=won`. Dashboard top row now shows **Total \| New \| Qualified \| Won** (aligned with Leads Management). |
| **Chart colors** | Each source key (including `import` vs `other`) gets a **distinct** color; unknown keys use a rotating palette. |
| **SEO** | `canonical`, `robots` meta, **Open Graph** + absolute `og:image`, **Twitter Card**, `lang="en-CA"`, **LocalBusiness JSON-LD** from `SiteSettings`. |
| **Discovery** | `/sitemap.xml` (public pages), `/robots.txt` (allows site, blocks `/dashboard/` and `/admin/`, points to sitemap). |
| **Performance** | Deferred scripts (jQuery → Bootstrap → `main.js`), hero `fetchpriority` + dimensions, below-fold images `loading="lazy"`. |
| **Production** | When `DEBUG=False`: `SECURE_SSL_REDIRECT`, HSTS, secure cookies, XSS/content-type headers (see `settings.py`). |

---

## Top 10 highest-impact actions (do these first)

1. **Set `DEBUG=False`** and correct **`ALLOWED_HOSTS`** + **`SITE_URL`** (https) in `.env` before going live.  
2. **PostgreSQL** (or managed DB) instead of SQLite for production concurrency and backups.  
3. **HTTPS everywhere** — Let’s Encrypt + Nginx; enable `SECURE_PROXY_SSL_HEADER` if TLS terminates at the proxy.  
4. **Run Lighthouse** (Chrome DevTools) on Home, Services, Contact — fix LCP (hero image size/format), CLS (reserve space for images/fonts).  
5. **Compress images** — WebP/AVIF for hero and fleet; keep fallbacks if needed.  
6. **Redis + caching** — Cache home/services views (`@cache_page` or template fragment cache) for anonymous users.  
7. **django-debug-toolbar** — Only in dev; profile duplicate queries and add `select_related` / `prefetch_related`.  
8. **Email** — Async queue (Celery/RQ) for notifications so requests stay fast.  
9. **Google Business Profile** — Match **NAP** (name, address, phone) with `SiteSettings` and footer.  
10. **Monitor** — Sentry or similar for 500s; log slow queries in staging.

---

## 1. Performance (why it feels slow)

| Cause | What to do |
|-------|------------|
| Large unoptimized images | Resize, WebP, `loading="lazy"` below the fold (partially done). |
| Many render-blocking CSS/JS | Defer scripts (done); consider splitting critical CSS. |
| SQLite under load | Move to PostgreSQL. |
| N+1 queries | Use `select_related` / `prefetch_related` (partially applied on dashboard). |
| No caching | Redis + per-view or full-page cache for public pages. |
| Static files | WhiteNoise + `CompressedManifestStaticFilesStorage` (already when `DEBUG=False`). |

**Tools:** Lighthouse, WebPageTest, Django Debug Toolbar (dev only).

---

## 2. SEO (ranking)

- **Titles** — Use `{% block title %}` / `meta_description` per page (services, contact, about).  
- **Headings** — One **H1** per page; logical H2/H3 (audit `home.html`, `services.html`, etc.).  
- **Internal links** — Footer + body links to Services, Contact, areas you serve.  
- **Location pages** — Add routes like `/locations/mississauga-delivery/` with unique copy (optional `core` views + templates).  
- **Reviews** — Keep testimonials visible; encourage Google reviews; match schema later with `Review` if you use structured data carefully.

---

## 3. Local SEO (GTA courier)

- Target phrases naturally: *same day delivery Toronto*, *GTA courier*, *business parcel delivery Mississauga*, etc.  
- **NAP** must match Google Business Profile and website footer.  
- Embed or link **Google Maps** (you already have contact map config).  
- **Blog or FAQ** — Answer “how much does same-day delivery cost in the GTA?” (unique text helps).

---

## 4. Core Web Vitals (short)

| Metric | Fix |
|--------|-----|
| **LCP** | Smaller/faster hero; `fetchpriority="high"`; proper width/height. |
| **CLS** | Width/height on images; avoid font swap layout shift (`font-display: swap` already on Google Fonts). |
| **INP / FID** | Less main-thread JS; defer non-critical scripts (done for base layout). |

---

## 5. Security and forms

- **HTTPS** + secure cookies (enabled when not `DEBUG`).  
- **CSRF** — Already on Django forms.  
- **CAPTCHA** — Add hCaptcha/reCAPTCHA on public lead forms if spam appears.  
- **Headers** — HSTS, `X-Frame-Options`, `X-Content-Type-Options` (partially via Django settings).

---

## 6. Deployment pattern

- **Gunicorn** (or uvicorn for ASGI) + **Nginx** reverse proxy, static via WhiteNoise or Nginx `alias`.  
- **Environment variables** — Never commit secrets; use `.env` on server.  
- **Backups** — DB + media; test restore.  
- **CDN** — Optional for `static/` and images.

---

## 7. Caching examples (when you add Redis)

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }
}

# views.py (public home)
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def home(request):
    ...
```

---

*Last updated: aligned with project templates and `parcel_delivery/settings.py`.*
