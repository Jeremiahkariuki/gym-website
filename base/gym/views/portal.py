from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import (
    Member, WorkoutPlan, DietPlan, Payment, MeasurementLog, GymClass,
    LibraryExercise, ProgressPhoto, Achievement, MemberAchievement, Announcement
)
from django import forms
from django.shortcuts import get_object_or_404

@login_required
def portal_dashboard(request):
    member = getattr(request.user, 'member_profile', None)
    if not member:
        # If they are staff but somehow reached here, send back to admin dash
        if request.user.is_staff:
            return redirect("dashboard")
        messages.error(request, "Your member profile is missing. Please contact support.")
        return redirect("home")
        
    active_membership = member.active_membership
    recent_payments = member.payments.all().order_by("-paid_on")[:5]
    
    # Health Progress Data
    measurements = member.measurements.all().order_by("date")
    chart_labels = [m.date.strftime("%b %d") for m in measurements]
    chart_weight = [float(m.weight) for m in measurements]
    chart_bmi = [float(m.bmi) for m in measurements if m.bmi]
    
    # Class Booking Data
    # Branches? Filter classes by member's branch
    available_classes = GymClass.objects.filter(branch=member.branch).select_related('trainer')
    enrolled_class_ids = member.enrolled_classes.values_list('id', flat=True)
    
    # Recent achievements
    recent_achievements = member.achievements_earned.select_related('achievement').order_by('-earned_on')[:3]
    
    # Announcements
    announcements = Announcement.objects.filter(is_active=True)[:3]
    
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
        "recent_achievements": recent_achievements,
        "announcements": announcements,
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
    category = request.GET.get('category')
    exercises = LibraryExercise.objects.all()
    if category:
        exercises = exercises.filter(category=category)
    
    # Use extremely short keys to prevent template tag splitting
    category_list = [{"i": c[0], "n": c[1]} for c in LibraryExercise.CATEGORY_CHOICES]
    
    return render(request, "gym/portal/exercise_library.html", {
        "exercises": exercises,
        "categories": category_list,
        "active_category": category
    })

class ProgressPhotoForm(forms.ModelForm):
    class Meta:
        model = ProgressPhoto
        fields = ['photo_before', 'photo_after', 'weight_at_time', 'notes']
        widgets = {
            'photo_before': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL to current photo'}),
            'photo_after': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL to previous/after photo (optional)'}),
            'weight_at_time': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

@login_required
def portal_progress_gallery(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    photos = member.progress_photos.all()
    
    if request.method == "POST":
        form = ProgressPhotoForm(request.POST)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.member = member
            photo.save()
            messages.success(request, "Progress photo added!")
            return redirect("portal_progress_gallery")
    else:
        form = ProgressPhotoForm()
        
    return render(request, "gym/portal/progress_history.html", {
        "photos": photos,
        "form": form
    })

class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['full_name', 'email', 'phone', 'address', 'fitness_goal', 'bio', 'medical_conditions', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fitness_goal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lose 5kg, Build Muscle'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

@login_required
def portal_profile_hub(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    if request.method == "POST":
        form = MemberProfileForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("portal_profile_hub")
    else:
        form = MemberProfileForm(instance=member)
        
    return render(request, "gym/portal/profile_hub.html", {
        "member": member,
        "form": form,
        "m_count": member.memberships.count(),
        "a_count": member.achievements_earned.count(),
        "m_email": member.email if member.email else "Not set"
    })

@login_required
def portal_achievement_room(request):
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return redirect("login")
        
    earned = member.achievements_earned.select_related('achievement').all()
    all_achievements = Achievement.objects.all()
    
    # Map earned achievements for easier lookup in template
    earned_ids = set(earned.values_list('achievement_id', flat=True))
    
    return render(request, "gym/portal/achievements.html", {
        "earned": earned,
        "all_achievements": all_achievements,
        "earned_ids": earned_ids
    })

@login_required
def portal_subscribe(request, plan_id):
    """
    Handles the 'Activate Now' flow from the portal.
    Supports prorated upgrades: if the member has an active, non-expired
    membership on a *different* plan, it calculates the unused-days credit
    and charges only the difference.
    """
    from ..models import MembershipPlan, Membership, Payment
    from django.utils import timezone
    from decimal import Decimal, ROUND_HALF_UP

    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        messages.error(request, "Please complete your member profile first.")
        return redirect("home")

    plan = get_object_or_404(MembershipPlan, id=plan_id)
    today = timezone.now().date()

    # ── Upgrade calculation helper ──────────────────────────────────────
    def _calc_upgrade(member, new_plan, today):
        """Return (upgrade_info_dict, net_amount) or (None, new_plan.price)."""
        active = member.memberships.filter(is_active=True).first()
        if not active or active.is_expired or active.plan_id == new_plan.id:
            return None, new_plan.price

        remaining_days = max((active.end_date - today).days, 0)
        if active.plan.duration_days > 0:
            daily_rate = active.plan.price / Decimal(active.plan.duration_days)
        else:
            daily_rate = Decimal("0.00")
        credit = (daily_rate * remaining_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        net = max(new_plan.price - credit, Decimal("0.00"))

        info = {
            "old_plan_name": active.plan.name,
            "old_plan_price": active.plan.price,
            "remaining_days": remaining_days,
            "daily_rate": daily_rate.quantize(Decimal("0.01")),
            "credit": credit,
            "net_amount": net,
            "is_upgrade": True,
        }
        return info, net

    upgrade_info, net_amount = _calc_upgrade(member, plan, today)

    if request.method == "POST":
        # Deactivate any existing active memberships
        Membership.objects.filter(member=member, is_active=True).update(is_active=False)

        # Create a fresh membership for the new plan
        membership = Membership.objects.create(
            member=member,
            plan=plan,
            start_date=today,
            is_active=True,
        )

        # Record payment with the (possibly prorated) net amount
        Payment.objects.create(
            member=member,
            amount=net_amount,
            method="Online Payment",
            Membership=membership,
            branch=member.branch,
        )

        if upgrade_info:
            messages.success(
                request,
                f"Upgraded to {plan.name}! Credit of KES {upgrade_info['credit']} "
                f"applied from your {upgrade_info['old_plan_name']} plan. "
                f"Charged KES {net_amount}."
            )
        else:
            messages.success(request, f"Successfully activated {plan.name}! Your payment was processed.")
        return redirect("portal_dashboard")

    context = {
        "member": member,
        "plan": plan,
        "upgrade_info": upgrade_info,
        "net_amount": net_amount,
    }
    return render(request, "gym/portal/checkout.html", context)

