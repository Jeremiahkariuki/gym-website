from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Member, WorkoutPlan, DietPlan, Payment, MeasurementLog, GymClass

@login_required
def portal_dashboard(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    active_membership = member.memberships.filter(is_active=True).first()
    recent_payments = member.payments.all().order_by("-paid_on")[:5]
    
    # Health Progress Data
    measurements = member.measurements.all().order_by("date")
    chart_labels = [m.date.strftime("%b %d") for m in measurements]
    chart_weight = [float(m.weight) for m in measurements]
    chart_bmi = [float(m.bmi) for m in measurements if m.bmi]
    
    # Class Booking Data
    available_classes = GymClass.objects.all().select_related('trainer')
    enrolled_class_ids = member.enrolled_classes.values_list('id', flat=True)
    
    return render(request, "gym/portal/dashboard.html", {
        "member": member,
        "active_membership": active_membership,
        "recent_payments": recent_payments,
        "measurements": measurements,
        "available_classes": available_classes,
        "enrolled_class_ids": enrolled_class_ids,
        "chart_labels": chart_labels,
        "chart_weight": chart_weight,
        "chart_bmi": chart_bmi,
    })

@login_required
def portal_notifications_optin(request):
    return render(request, "gym/portal/notifications_optin.html")


@login_required
def portal_class_toggle(request, class_id):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    gym_class = get_object_or_404(GymClass, id=class_id)
    if gym_class.members.filter(id=member.id).exists():
        gym_class.members.remove(member)
        messages.info(request, f"You have left the {gym_class.name} class.")
    else:
        gym_class.members.add(member)
        messages.success(request, f"You have successfully joined the {gym_class.name} class!")
    return redirect("portal_dashboard")

@login_required
def portal_workout(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    workout_plans = member.workout_plans.all()
    return render(request, "gym/portal/workout.html", {
        "member": member,
        "workout_plans": workout_plans,
    })

@login_required
def portal_diet(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    try:
        diet_plan = member.diet_plan
    except DietPlan.DoesNotExist:
        diet_plan = None
        
    return render(request, "gym/portal/diet.html", {
        "member": member,
        "diet_plan": diet_plan,
    })

@login_required
def portal_payments(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    payments = member.payments.all().order_by("-paid_on")
    return render(request, "gym/portal/payments.html", {
        "member": member,
        "payments": payments,
    })

@login_required
def portal_id_card(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    return render(request, "gym/portal/id_card.html", {
        "member": member,
    })

@login_required
def portal_exercise_library(request):
    return render(request, "gym/portal/exercise_library.html")

@login_required
def portal_progress_gallery(request):
    return render(request, "gym/portal/progress_history.html")

@login_required
def portal_profile_hub(request):
    return render(request, "gym/portal/profile_hub.html")

@login_required
def portal_achievement_room(request):
    return render(request, "gym/portal/achievements.html")

