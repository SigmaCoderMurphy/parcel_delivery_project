# Production Deployment Guide (Ubuntu + Nginx + Gunicorn)

This guide deploys the project on an Ubuntu VPS with PostgreSQL (recommended), Gunicorn, Nginx, HTTPS, static/media serving, and safe restart steps.

## 1) Server bootstrap

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git certbot python3-certbot-nginx
```

Optional but recommended for database:

```bash
sudo apt install -y postgresql postgresql-contrib
```

## 2) App user + project directory

```bash
sudo adduser --system --group --home /opt/parcel_delivery parcel
sudo mkdir -p /opt/parcel_delivery/app
sudo chown -R parcel:parcel /opt/parcel_delivery
```

## 3) Clone and Python environment

```bash
sudo -u parcel -H bash -c '
cd /opt/parcel_delivery/app
git clone <YOUR_REPO_URL> .
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
'
```

## 4) Environment variables

Create `/opt/parcel_delivery/app/.env` (never commit this):

```env
DEBUG=False
SECRET_KEY=<long-random-secret>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SITE_URL=https://yourdomain.com
ADMIN_URL=secure-admin-path/
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...

BREVO_API_KEY=...
BREVO_SENDER_EMAIL=...
BREVO_SENDER_NAME=Eastern Logistics
```

## 5) Database setup and migrations

If using PostgreSQL, create DB/user first, then configure `DATABASE_URL` / DB settings in Django.

Then run:

```bash
sudo -u parcel -H bash -c '
cd /opt/parcel_delivery/app
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
'
```

## 6) Gunicorn systemd service

Create `/etc/systemd/system/parcel_delivery.service`:

```ini
[Unit]
Description=Parcel Delivery Django (Gunicorn)
After=network.target

[Service]
User=parcel
Group=www-data
WorkingDirectory=/opt/parcel_delivery/app
Environment="PATH=/opt/parcel_delivery/app/.venv/bin"
ExecStart=/opt/parcel_delivery/app/.venv/bin/gunicorn parcel_delivery.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable/start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable parcel_delivery
sudo systemctl start parcel_delivery
sudo systemctl status parcel_delivery
```

## 7) Nginx reverse proxy + static/media + compression/cache

Create `/etc/nginx/sites-available/parcel_delivery`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 25M;

    location /static/ {
        alias /opt/parcel_delivery/app/staticfiles/;
        expires 365d;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location /media/ {
        alias /opt/parcel_delivery/app/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript application/xml image/svg+xml;
    gzip_min_length 1024;
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/parcel_delivery /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 8) SSL/HTTPS (Let’s Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Auto-renew test:

```bash
sudo certbot renew --dry-run
```

## 9) Safe deploy/restart workflow

For every release:

```bash
sudo -u parcel -H bash -c '
cd /opt/parcel_delivery/app
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
'
sudo systemctl restart parcel_delivery
sudo systemctl reload nginx
```

## 10) Operational data purge (requested cleanup)

Dry-run first:

```bash
python manage.py purge_operational_data --confirm --dry-run
```

Execute destructive purge:

```bash
python manage.py purge_operational_data --confirm
```

This deletes:
- all users (including superusers/staff)
- all leads
- quotes, follow-ups, communication logs, call logs, scheduled emails (via cascade)

It keeps:
- services
- testimonials
- site settings

## 11) Production verification checklist

- `python manage.py check --deploy` returns clean.
- `/sitemap.xml` and `/robots.txt` load successfully.
- Homepage and services pages show no broken images.
- Lead form submits and confirmation email is delivered.
- Admin available only on custom `ADMIN_URL`.
- Static and media URLs are served by Nginx.
- SSL certificate is valid.
