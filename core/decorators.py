"""Access control for dashboard and sensitive views."""
from functools import wraps

from django.shortcuts import redirect


def superuser_required(view_func):
    """Superadmin only (Django `is_superuser`)."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("admin:login")
        if not request.user.is_superuser:
            return redirect("access_denied")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def staff_required(view_func):
    """
    Admin / staff (Django `is_staff`): full operational dashboard.
    Superusers always pass.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("admin:login")
        if not request.user.is_staff:
            return redirect("access_denied")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def login_required_user(view_func):
    """
    Any authenticated account (role `user` or above).
    Use for future staff-adjacent pages that are not `is_staff`.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("admin:login")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
