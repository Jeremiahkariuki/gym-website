from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Member, WorkoutPlan, DietPlan, Payment

@login_required
def portal_dashboard(request):
    member = get_object_or_404(Member, user=request.user)
    active_membership = member.memberships.filter(is_active=True).first()
    recent_payments = member.payments.all().order_by("-paid_on")[:5]
    
    return render(request, "gym/portal/dashboard.html", {
        "member": member,
        "active_membership": active_membership,
        "recent_payments": recent_payments,
    })

@login_required
def portal_workout(request):
    member = get_object_or_404(Member, user=request.user)
    workout_plans = member.workout_plans.all()
    return render(request, "gym/portal/workout.html", {
        "member": member,
        "workout_plans": workout_plans,
    })

@login_required
def portal_diet(request):
    member = get_object_or_404(Member, user=request.user)
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
    member = get_object_or_404(Member, user=request.user)
    payments = member.payments.all().order_by("-paid_on")
    return render(request, "gym/portal/payments.html", {
        "member": member,
        "payments": payments,
    })
