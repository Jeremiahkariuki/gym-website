from django.contrib import messages
from django.shortcuts import redirect, render

from ..models import MembershipPlan, GymClass, ContactMessage, Announcement, GymPhoto, Membership

def home_view(request):
    """
    Intelligent Home Experience.
    If logged in, acts as a dispatcher to the appropriate role dashboard.
    If anonymous, shows the public marketing page.
    """
    # --- Public Landing Page Logic ---
    plans = MembershipPlan.objects.all().order_by("price")
    featured_classes = GymClass.objects.all()[:3]
    announcements = Announcement.objects.filter(is_active=True)[:3]
    gallery = GymPhoto.objects.all()[:6]

    active_membership = None
    if request.user.is_authenticated:
        member = getattr(request.user, 'member_profile', None)
        if member:
            active_membership = member.memberships.filter(is_active=True).first()

    # Add frequency labels and active status to plans
    for plan in plans:
        # Determine frequency label
        if plan.duration_days == 1: plan.freq_label = "Daily"
        elif plan.duration_days == 7: plan.freq_label = "Weekly"
        elif plan.duration_days <= 31: plan.freq_label = "Monthly"
        elif plan.duration_days >= 360: plan.freq_label = "Yearly"
        else: plan.freq_label = "Select Plan"
        
        # Determine if it's the user's active plan
        plan.is_active = active_membership and plan.id == active_membership.plan.id

    return render(request, "gym/home.html", {
        "plans": plans,
        "featured_classes": featured_classes,
        "announcements": announcements,
        "gallery": gallery,
        "active_membership": active_membership,
    })


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
