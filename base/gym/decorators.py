from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """
    Only allow is_staff users.
    Redirects unauthenticated users to the custom login page.
    Redirects authenticated non-staff users to their dashboard-redirect.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_staff:
            return redirect("login_redirect")
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_or_trainer_required(view_func):
    """
    Allow access for staff (admins) and trainers.
    Redirects unauthenticated users to custom login.
    Redirects regular members to their portal dashboard.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        if hasattr(request.user, 'trainer_profile'):
            return view_func(request, *args, **kwargs)
        # Regular member — not allowed
        messages.error(request, "You don't have permission to access this page.")
        return redirect("portal_dashboard")
    return wrapper
