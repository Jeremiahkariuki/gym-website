from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Attedance, MembershipPlan, Membership, Payment
from django.utils import timezone
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.db import models
from .forms import PlanForm
from datetime import timedelta

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "phone", "email", "address"]


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["member", "plan", "start_date"]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "Membership", "amount", "method", "reference"]

@login_required
def member_list(request):
    members = Member.objects.all().order_by("-joined_on")
    return render(request, "gym/member_list.html", {"members": members})

@login_required
def member_create(request):
    if request.method =="POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("member_list")
    else:
        form = MemberForm()
    return render(request, "gym/member_form.html", {"form": form})


@login_required
def member_edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect("member_list")
    else:
        form = MemberForm(instance=member)
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
    today_attedance = Attedance.objects.filter(date=today).count()
    present_today = Attedance.objects.filter(date=today).select_related("member")

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

    Attedance.objects.get_or_create(member=member, date=today)
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


@login_required
def member_detail(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    memberships = member.memberships.all()
    payments = member.payments.all()
    attendance = member.attedance_set.all().order_by("-date")[:30]
    
    return render(request, "gym/member_detail.html", {
        "member": member,
        "memberships": memberships,
        "payments": payments,
        "attendance": attendance,
    })


@login_required
def assign_membership(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.member = member
            membership.save()
            return redirect("member_detail", member_id=member.id)
    else:
        form = MembershipForm(initial={"member": member})
    
    return render(request, "gym/membership_form.html", {"form": form, "member": member})


@login_required
def record_payment(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("member_detail", member_id=member.id)
    else:
        form = PaymentForm(initial={"member": member})
    
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
    
    payment_methods = Payment.objects.values("method").annotate(
        total=models.Sum("amount"), 
        count=models.Count("id")
    )
    
    return render(request, "gym/revenue_report.html", {
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "payment_methods": payment_methods,
        "month": this_month.strftime("%B %Y"),
    })