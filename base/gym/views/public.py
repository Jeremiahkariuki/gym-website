from django.contrib import messages
from django.shortcuts import redirect, render

from ..models import MembershipPlan, GymClass, ContactMessage, Announcement, GymPhoto, Membership

def home_view(request):
    """
    Intelligent Home Experience.
    If logged in, acts as a dispatcher to the appropriate role dashboard.
    If anonymous, shows the public marketing page.
    """
    if not request.user.is_authenticated:
        # --- Public Landing Page Logic ---
        plans = MembershipPlan.objects.all().order_by("price")
        featured_classes = GymClass.objects.all()[:3]
        announcements = Announcement.objects.filter(is_active=True)[:3]
        gallery = GymPhoto.objects.all()[:6]

        return render(request, "gym/home.html", {
            "plans": plans,
            "featured_classes": featured_classes,
            "announcements": announcements,
            "gallery": gallery,
        })
    
    # --- Authenticated User Dispatcher ---
    # We use the same logic as login_redirect_view
    from .auth import login_redirect_view
    return login_redirect_view(request)


def class_schedule_view(request):
    """Displays the full week schedule."""
    # Organize classes by day
    classes_by_day = {}
    for day_id, day_name in GymClass.DAYS:
        classes_by_day[day_name] = GymClass.objects.filter(day=day_id).select_related("trainer__user")
    
    return render(request, "gym/classes.html", {
        "classes_by_day": classes_by_day
    })

def contact_view(request):
    """Handles the contact form."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Your message has been sent. We'll get back to you soon!")
            return redirect("contact")
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, "gym/contact.html")
