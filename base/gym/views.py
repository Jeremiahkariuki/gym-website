from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Attedance, MembershipPlan
from django.utils import timezone
from django  import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from .forms import PlanForm

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "phone", "email", "address"]

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


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("member_list")

    return render(request, "accounts/login.html")


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
    today  = timezone.now().date()

    Attedance .objects.get_or_create(member=member, date=today)
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

        return render(request, "gym/plan_form.html", {"form" : form })
    
