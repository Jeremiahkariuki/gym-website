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

    # Add active status to plans
    for plan in plans:
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


def class_events_api(request):
    """
    Returns JSON array of scheduled gym classes for calendar visualization.
    Generates dynamic events for current & upcoming week based on recurring days.
    """
    from django.http import JsonResponse
    import datetime

    member = None
    enrolled_ids = set()
    if request.user.is_authenticated:
        member = getattr(request.user, 'member_profile', None)
        if member:
            enrolled_ids = set(member.enrolled_classes.values_list('id', flat=True))

    classes = GymClass.objects.select_related("trainer__user", "branch").prefetch_related("members").all()

    today = timezone.now().date()
    # Find start of current week (Monday)
    start_of_week = today - datetime.timedelta(days=today.weekday())

    events = []

    # Generate recurring events for 6 weeks (-2 to +3 weeks)
    for week_offset in range(-2, 4):
        week_start = start_of_week + datetime.timedelta(weeks=week_offset)
        for c in classes:
            class_date = week_start + datetime.timedelta(days=c.day)
            start_iso = f"{class_date.isoformat()}T{c.start_time.strftime('%H:%M:%S')}"
            end_iso = f"{class_date.isoformat()}T{c.end_time.strftime('%H:%M:%S')}"

            is_enrolled = c.id in enrolled_ids
            members_count = c.members.count()

            events.append({
                "id": f"{c.id}-{class_date.isoformat()}",
                "class_id": c.id,
                "title": c.name,
                "start": start_iso,
                "end": end_iso,
                "trainer": c.trainer.full_name if c.trainer else "Expert Trainer",
                "description": c.description or "High intensity training session.",
                "branch": c.branch.name if c.branch else "Main Branch",
                "is_enrolled": is_enrolled,
                "members_count": members_count,
                "backgroundColor": "#10b981" if is_enrolled else "#3b82f6",
                "borderColor": "#059669" if is_enrolled else "#2563eb",
            })

    return JsonResponse(events, safe=False)

