from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Attedance, MembershipPlan, Membership, Payment, Expense, MeasurementLog, DietPlan, WorkoutPlan, Exercise
from django.utils import timezone
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.db import models
from .forms import PlanForm, MembershipForm, PaymentForm, ExpenseForm, MeasurementLogForm, DietPlanForm, WorkoutPlanForm, ExerciseForm
from datetime import timedelta

class MemberForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        label="Membership Plan",
        required=True,
        empty_label="--- Select a Plan ---",
        help_text="A starting membership plan is required for all new members.",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Member
        fields = ["full_name", "phone", "email", "address"]


@login_required
def member_list(request):
    members = Member.objects.select_related("diet_plan").prefetch_related("memberships__plan").all().order_by("-joined_on")
    return render(request, "gym/member_list.html", {"members": members})

@login_required
def member_create(request):
    if request.method =="POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            plan = form.cleaned_data.get('plan')
            if plan:
                Membership.objects.create(
                    member=member,
                    plan=plan,
                    is_active=True,
                    start_date=timezone.now()
                )
            messages.success(request, "Member added successfully.")
            return redirect("member_list")
    else:
        form = MemberForm()
    return render(request, "gym/member_form.html", {"form": form})


@login_required
def member_edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    active_membership = member.memberships.filter(is_active=True).first()

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            plan = form.cleaned_data.get('plan')

            if plan:
                if not active_membership or active_membership.plan != plan:
                    if active_membership:
                        active_membership.is_active = False
                        active_membership.save()
                    Membership.objects.create(
                        member=member,
                        plan=plan,
                        is_active=True,
                        start_date=timezone.now()
                    )
            elif active_membership and not plan:
                active_membership.is_active = False
                active_membership.save()

            messages.success(request, "Member updated successfully.")
            return redirect("member_list")
    else:
        initial_data = {}
        if active_membership:
            initial_data['plan'] = active_membership.plan
        form = MemberForm(instance=member, initial=initial_data)
        
    return render(request, "gym/member_form.html", {"form": form, "member": member})


@login_required
def member_delete(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        member.delete()
        return redirect("member_list")
    return render(request, "gym/member_confirm_delete.html", {"member": member})


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Enter your username",
            "class": "form-control"
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Enter your password",
            "class": "form-control"
        })

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}))

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have professional placeholders
        placeholders = {
            "username": "Choose a username",
            "email": "Enter your email address",
            "password1": "Create a strong password",
            "password2": "Confirm your password",
        }
        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"placeholder": placeholder})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(request, "gym/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    today = timezone.now().date()
    this_month = timezone.now().month

    total_members= Member.objects.count()
    members_joined_today = Member.objects.filter(joined_on=today).count()
    today_attedance = Attedance.objects.filter(date__date=today).count()
    present_today = Attedance.objects.filter(date__date=today).select_related("member")

    return render(request, "gym/dashboard.html", {
        "today" : today,
        "this_month" : this_month,
        "total_members" : total_members,
        "members_joined_today" : members_joined_today,
        "today_attedance" : today_attedance,
        "present_today" : present_today,
    })

@login_required 
def mark_present(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    today = timezone.now().date()

    # Only create if they haven't checked in today yet
    if not Attedance.objects.filter(member=member, date__date=today).exists():
        Attedance.objects.create(member=member, date=timezone.now())
        
    return redirect("dashboard")

def plan_list(request):
    plans = MembershipPlan.objects.all().order_by("price")
    return render(request, "gym/plan_list.html", {"plans": plans})

def plan_create(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("plan_list")
    else:
        form = PlanForm()
    
    return render(request, "gym/plan_form.html", {"form": form})


def plan_edit(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership Plan updated successfully.")
            return redirect("plan_list")
    else:
        form = PlanForm(instance=plan)
        
    return render(request, "gym/plan_form.html", {"form": form})


def plan_delete(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Membership Plan deleted successfully.")
        return redirect("plan_list")
        
    return render(request, "gym/plan_confirm_delete.html", {"plan": plan})


@login_required
def member_detail(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    memberships = member.memberships.all()
    payments = member.payments.all()
    attendance = member.attedance_set.all().order_by("-date")[:30]
    
    measurements = member.measurements.all().order_by("-date")
    try:
        diet_plan = member.diet_plan
    except:
        diet_plan = None
    workout_plans = member.workout_plans.all()
    
    return render(request, "gym/member_detail.html", {
        "member": member,
        "memberships": memberships,
        "payments": payments,
        "attendance": attendance,
        "measurements": measurements,
        "diet_plan": diet_plan,
        "workout_plans": workout_plans,
    })


@login_required
def assign_membership(request, member_id):
    member = get_object_or_404(Member, id=member_id)

    # Prevent a member from receiving a second active membership
    if request.method == "GET" and member.memberships.filter(is_active=True).exists():
        messages.error(request, "This member already has an active membership.")
        return redirect("member_detail", member_id=member.id)
    
    if request.method == "POST":
        if member.memberships.filter(is_active=True).exists():
            messages.error(request, "This member already has an active membership.")
            return redirect("member_detail", member_id=member.id)
            
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.member = member
            membership.save()
            messages.success(request, "Membership assigned successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = MembershipForm(initial={"member": member})
    
    return render(request, "gym/membership_form.html", {"form": form, "member": member})


@login_required
def record_payment(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == "POST":
        form = PaymentForm(request.POST, member=member)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.member = member
            
            # Automatically link to or activate the selected plan
            plan = form.cleaned_data.get('plan')
            if plan:
                membership, created = Membership.objects.get_or_create(
                    member=member,
                    plan=plan,
                    is_active=True,
                    defaults={'start_date': timezone.now()}
                )
                payment.Membership = membership
                
            payment.save()
            messages.success(request, "Payment recorded successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = PaymentForm(member=member)
    
    return render(request, "gym/payment_form.html", {"form": form, "member": member})


@login_required
def attendance_report(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    
    attendance_data = Attedance.objects.filter(
        date__gte=last_7_days
    ).values("member__full_name").annotate(
        count=models.Count("id")
    ).order_by("-count")
    
    total_attendance = Attedance.objects.count()
    unique_members = Attedance.objects.values("member").distinct().count()
    
    return render(request, "gym/attendance_report.html", {
        "attendance_data": attendance_data,
        "total_attendance": total_attendance,
        "unique_members": unique_members,
        "period": f"Last 7 days (from {last_7_days} to {today})",
    })


@login_required
def revenue_report(request):
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    total_revenue = Payment.objects.aggregate(
        total=models.Sum("amount")
    )["total"] or 0
    
    monthly_revenue = Payment.objects.filter(
        date__gte=this_month
    ).aggregate(
        total=models.Sum("amount")
    )["total"] or 0
    
    total_expenses = Expense.objects.aggregate(total=models.Sum("amount"))["total"] or 0
    monthly_expenses = Expense.objects.filter(date__gte=this_month).aggregate(total=models.Sum("amount"))["total"] or 0

    payment_methods = Payment.objects.values("method").annotate(
        total=models.Sum("amount"), 
        count=models.Count("id")
    )

    # Fetch all members and determine their payment status for this month
    members = Member.objects.all().prefetch_related('payments', 'memberships__plan')
    member_status = []
    
    for member in members:
        has_paid = member.payments.filter(date__gte=this_month).exists()
        active_membership = member.memberships.filter(is_active=True).first()
        plan_name = active_membership.plan.name if active_membership else "No Active Plan"
        
        member_status.append({
            'member': member,
            'has_paid': has_paid,
            'plan_name': plan_name,
        })
    
    return render(request, "gym/revenue_report.html", {
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "total_expenses": total_expenses,
        "monthly_expenses": monthly_expenses,
        "monthly_profit": monthly_revenue - monthly_expenses,
        "total_profit": total_revenue - total_expenses,
        "payment_methods": payment_methods,
        "month": this_month.strftime("%B %Y"),
        "member_status": member_status,
    })

@login_required
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    member = membership.member
    next_url = request.POST.get("next_url") or request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    
    if request.method == "POST":
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership updated successfully.")
            return redirect(next_url) if next_url else redirect("member_detail", member_id=member.id)
    else:
        form = MembershipForm(instance=membership)
    return render(request, "gym/membership_form.html", {"form": form, "member": member, "next_url": next_url})

@login_required
def membership_delete(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    member = membership.member
    if request.method == "POST":
        membership.delete()
        messages.success(request, "Membership deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(request, "gym/membership_confirm_delete.html", {"membership": membership, "member": member})

@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    member = payment.member
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Automatically link to or activate the newly selected plan if changed
            plan = form.cleaned_data.get('plan')
            if plan:
                membership, created = Membership.objects.get_or_create(
                    member=member,
                    plan=plan,
                    is_active=True,
                    defaults={'start_date': timezone.now()}
                )
                payment.Membership = membership
                
            payment.save()
            messages.success(request, "Payment updated successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        # Pre-fill the dropdown with their actual assigned plan instead of blank
        initial_data = {}
        if payment.Membership and payment.Membership.plan:
            initial_data['plan'] = payment.Membership.plan.id
        form = PaymentForm(instance=payment, initial=initial_data)
        
    return render(request, "gym/payment_form.html", {"form": form, "member": member})

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    member = payment.member
    if request.method == "POST":
        payment.delete()
        messages.success(request, "Payment deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(request, "gym/payment_confirm_delete.html", {"payment": payment, "member": member})


@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by("-date")
    return render(request, "gym/expense_list.html", {"expenses": expenses})

@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense added successfully.")
            return redirect("expense_list")
    else:
        form = ExpenseForm()
    return render(request, "gym/expense_form.html", {"form": form})

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully.")
            return redirect("expense_list")
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "gym/expense_form.html", {"form": form})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully.")
        return redirect("expense_list")
    return render(request, "gym/expense_confirm_delete.html", {"expense": expense})

@login_required
def measurement_create(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = MeasurementLogForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.member = member
            measurement.save()
            messages.success(request, "Measurement recorded successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = MeasurementLogForm()
    return render(request, "gym/measurement_form.html", {"form": form, "member": member})

@login_required
def measurement_delete(request, pk):
    measurement = get_object_or_404(MeasurementLog, pk=pk)
    member = measurement.member
    if request.method == "POST":
        measurement.delete()
        messages.success(request, "Measurement deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(request, "gym/measurement_confirm_delete.html", {"measurement": measurement, "member": member})

@login_required
def diet_plan_edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    diet_plan, created = DietPlan.objects.get_or_create(member=member, defaults={'calories': 2000})
    if request.method == "POST":
        form = DietPlanForm(request.POST, instance=diet_plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Diet plan updated successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = DietPlanForm(instance=diet_plan)
    return render(request, "gym/diet_plan_form.html", {"form": form, "member": member})

@login_required
def workout_plan_create(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.member = member
            workout.save()
            messages.success(request, "Workout plan created successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = WorkoutPlanForm()
    return render(request, "gym/workout_plan_form.html", {"form": form, "member": member})

@login_required
def workout_plan_detail(request, pk):
    workout = get_object_or_404(WorkoutPlan, pk=pk)
    member = workout.member
    exercises = workout.exercises.all()
    
    days_dict = {i: {"name": name, "exercises": []} for i, name in Exercise.DAYS}
    for ex in exercises:
        days_dict[ex.day]["exercises"].append(ex)
        
    return render(request, "gym/workout_plan_detail.html", {
        "workout": workout, 
        "member": member, 
        "days_dict": days_dict
    })

@login_required
def workout_plan_delete(request, pk):
    workout = get_object_or_404(WorkoutPlan, pk=pk)
    member = workout.member
    if request.method == "POST":
        workout.delete()
        messages.success(request, "Workout plan deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(request, "gym/workout_plan_confirm_delete.html", {"workout": workout, "member": member})

@login_required
def exercise_create(request, workout_id):
    workout = get_object_or_404(WorkoutPlan, id=workout_id)
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.workout_plan = workout
            exercise.save()
            messages.success(request, "Exercise added successfully.")
            return redirect("workout_plan_detail", pk=workout.id)
    else:
        form = ExerciseForm(initial={"day": request.GET.get('day', 0)})
    return render(request, "gym/exercise_form.html", {"form": form, "workout": workout})

@login_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    workout = exercise.workout_plan
    if request.method == "POST":
        exercise.delete()
        messages.success(request, "Exercise deleted successfully.")
        return redirect("workout_plan_detail", pk=workout.id)
    return render(request, "gym/exercise_confirm_delete.html", {"exercise": exercise})
