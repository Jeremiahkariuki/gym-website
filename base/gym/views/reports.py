from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import Attedance, Member


@login_required
def dashboard(request):
    today = timezone.now().date()
    this_month = timezone.now().month

    total_members = Member.objects.count()
    members_joined_today = Member.objects.filter(joined_on=today).count()
    today_attedance = Attedance.objects.filter(date=today).count()
    present_today = Attedance.objects.filter(date=today).select_related("member")

    return render(
        request,
        "gym/dashboard.html",
        {
            "today": today,
            "this_month": this_month,
            "total_members": total_members,
            "members_joined_today": members_joined_today,
            "today_attedance": today_attedance,
            "present_today": present_today,
        },
    )


@login_required
def mark_present(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    today = timezone.now().date()

    # Only create if they haven't checked in today yet (unique_together now enforces this too)
    Attedance.objects.get_or_create(member=member, date=today)

    return redirect("dashboard")


@login_required
def attendance_report(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)

    attendance_data = (
        Attedance.objects.filter(date__gte=last_7_days)
        .values("member__full_name")
        .annotate(count=db_models.Count("id"))
        .order_by("-count")
    )

    total_attendance = Attedance.objects.count()
    unique_members = Attedance.objects.values("member").distinct().count()

    return render(
        request,
        "gym/attendance_report.html",
        {
            "attendance_data": attendance_data,
            "total_attendance": total_attendance,
            "unique_members": unique_members,
            "period": f"Last 7 days (from {last_7_days} to {today})",
        },
    )
