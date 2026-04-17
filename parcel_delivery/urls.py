"""
URL configuration for parcel_delivery project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from core.forms import CustomPasswordResetForm

admin_prefix = settings.ADMIN_URL.rstrip("/")

# Password reset for admin/staff users (must be registered before admin.site.urls).
# Admin login shows "Forgotten your login credentials?" when admin_password_reset resolves.
urlpatterns = [
    path(
        f'{admin_prefix}/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.txt',
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
            form_class=CustomPasswordResetForm,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None)
            or getattr(settings, "SITE_EMAIL", ""),
            extra_email_context={
                "site_url": getattr(settings, "SITE_URL", ""),
            },
        ),
        name='admin_password_reset',
    ),
    path(
        f'{admin_prefix}/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('core.urls')),
    path('dashboard/', include('leads.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler404 = "core.views.handler404"
handler500 = "core.views.handler500"