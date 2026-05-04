from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import MembershipPlan, GymClass, ContactMessage

def home_view(request):
    """Public landing page."""
    plans = MembershipPlan.objects.all()
    # Top 3 classes for preview
    featured_classes = GymClass.objects.all()[:3]
    return render(request, "gym/home.html", {
        "plans": plans,
        "featured_classes": featured_classes
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
