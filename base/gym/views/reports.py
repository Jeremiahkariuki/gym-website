from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import Attendance, Member, Membership, ContactMessage, Equipment


@login_required
def dashboard(request):
    today = timezone.now().date()
    this_month = timezone.now().month

    active_branch_id = request.session.get('active_branch_id')
    
    total_members = Member.objects.all()
    members_joined_today_query = Member.objects.filter(joined_on=today)
    today_attendance_query = Attendance.objects.filter(date=today)
    
    if active_branch_id:
        total_members = total_members.filter(branch_id=active_branch_id)
        members_joined_today_query = members_joined_today_query.filter(branch_id=active_branch_id)
        today_attendance_query = today_attendance_query.filter(branch_id=active_branch_id)

    total_members_count = total_members.count()
    members_joined_today = members_joined_today_query.count()
    today_attendance = today_attendance_query.count()
    present_today = today_attendance_query.select_related("member")
    
    # Calculate memberships expiring in the next 7 days
    seven_days_from_now = today + timedelta(days=7)
    # Calculate memberships expiring soon
    seven_days_from_now = today + timedelta(days=7)
    expiring_soon = Membership.objects.filter(
        is_active=True,
        end_date__isnull=False,
        end_date__gte=today,
        end_date__lte=seven_days_from_now
    ).select_related("member", "plan")

    if active_branch_id:
        expiring_soon = expiring_soon.filter(member__branch_id=active_branch_id)
    
    expiring_soon = expiring_soon.order_by("end_date")
    
    # Recent Contact Messages
    recent_messages = ContactMessage.objects.all().order_by("-created_at")[:5]
    
    # Equipment requiring maintenance
    maintenance_required = Equipment.objects.filter(status="maintenance")
    if active_branch_id:
        maintenance_required = maintenance_required.filter(branch_id=active_branch_id)

    return render(
        request,
        "gym/dashboard.html",
        {
            "today": today,
            "this_month": this_month,
            "total_members": total_members_count,
            "members_joined_today": members_joined_today,
            "today_attendance": today_attendance,
            "present_today": present_today,
            "expiring_soon": expiring_soon,
            "active_branch_id": active_branch_id,
            "recent_messages": recent_messages,
            "maintenance_required": maintenance_required,
        },
    )


@login_required
def mark_present(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    today = timezone.now().date()

    # Only create if they haven't checked in today yet (unique_together now enforces this too)
    # Only create if they haven't checked in today yet
    active_branch_id = request.session.get('active_branch_id')
    Attendance.objects.get_or_create(
        member=member, 
        date=today,
        defaults={'branch_id': active_branch_id or member.branch_id}
    )

    return redirect("dashboard")


@login_required
def attendance_report(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)

    attendance_data = (
        Attendance.objects.filter(date__gte=last_7_days)
        .values("member__full_name")
        .annotate(count=db_models.Count("id"))
        .order_by("-count")
    )

    total_attendance = Attendance.objects.count()
    unique_members = Attendance.objects.values("member").distinct().count()

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
