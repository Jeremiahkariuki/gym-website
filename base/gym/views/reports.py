from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .trainers import Trainer
from ..decorators import admin_required, staff_or_trainer_required

import json
from ..models import Attendance, Member, Membership, ContactMessage, Equipment, TrainerAssignment, Payment, Expense, MembershipPlan


@staff_or_trainer_required
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
    
    # Active memberships count
    active_memberships_qs = Membership.objects.filter(is_active=True)
    if active_branch_id:
        active_memberships_qs = active_memberships_qs.filter(member__branch_id=active_branch_id)
    active_members_count = active_memberships_qs.values('member').distinct().count()

    # Calculate memberships expiring in the next 7 days
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
    maintenance_required = Equipment.objects.filter(status__iexact="maintenance")
    if active_branch_id:
        maintenance_required = maintenance_required.filter(branch_id=active_branch_id)
    
    # Pending Trainer Assignments
    pending_assignments = TrainerAssignment.objects.filter(status="pending").select_related("member", "trainer")
    if active_branch_id:
        pending_assignments = pending_assignments.filter(member__branch_id=active_branch_id)

    # Calculate income & expenses
    payments_qs = Payment.objects.all()
    expenses_qs = Expense.objects.all()
    if active_branch_id:
        payments_qs = payments_qs.filter(branch_id=active_branch_id)
        expenses_qs = expenses_qs.filter(branch_id=active_branch_id)
    
    total_income = payments_qs.aggregate(total=db_models.Sum("amount"))["total"] or 0
    monthly_income = (
        payments_qs.filter(date__year=today.year, date__month=today.month)
        .aggregate(total=db_models.Sum("amount"))["total"] or 0
    )
    monthly_expenses = (
        expenses_qs.filter(date__year=today.year, date__month=today.month)
        .aggregate(total=db_models.Sum("amount"))["total"] or 0
    )
    net_monthly_profit = monthly_income - monthly_expenses

    # --- Analytics & Chart Aggregations ---
    # 1. 7-Day Attendance Trend
    attendance_days = []
    attendance_counts = []
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_name = day_date.strftime("%a")
        att_qs = Attendance.objects.filter(date=day_date)
        if active_branch_id:
            att_qs = att_qs.filter(branch_id=active_branch_id)
        attendance_days.append(day_name)
        attendance_counts.append(att_qs.count())

    # 2. Membership Plan Distribution
    plan_qs = MembershipPlan.objects.all()
    plan_labels = []
    plan_counts = []
    for plan in plan_qs:
        m_qs = Membership.objects.filter(plan=plan, is_active=True)
        if active_branch_id:
            m_qs = m_qs.filter(member__branch_id=active_branch_id)
        count = m_qs.count()
        if count > 0:
            plan_labels.append(plan.name)
            plan_counts.append(count)
    if not plan_labels:
        plan_labels = ["No Active Plans"]
        plan_counts = [1]

    # 3. Last 6 Months Income vs Expenses
    monthly_labels = []
    monthly_income_data = []
    monthly_expense_data = []
    for i in range(5, -1, -1):
        y = today.year
        m = today.month - i
        if m <= 0:
            m += 12
            y -= 1
        m_date = timezone.datetime(y, m, 1)
        monthly_labels.append(m_date.strftime("%b"))
        
        inc_q = Payment.objects.filter(date__year=y, date__month=m)
        exp_q = Expense.objects.filter(date__year=y, date__month=m)
        if active_branch_id:
            inc_q = inc_q.filter(branch_id=active_branch_id)
            exp_q = exp_q.filter(branch_id=active_branch_id)
        monthly_income_data.append(float(inc_q.aggregate(t=db_models.Sum("amount"))["t"] or 0))
        monthly_expense_data.append(float(exp_q.aggregate(t=db_models.Sum("amount"))["t"] or 0))

    return render(
        request,
        "gym/dashboard.html",
        {
            "today": today,
            "this_month": this_month,
            "total_members": total_members_count,
            "active_members_count": active_members_count,
            "members_joined_today": members_joined_today,
            "today_attendance": today_attendance,
            "present_today": present_today,
            "expiring_soon": expiring_soon,
            "expiring_soon_count": expiring_soon.count(),
            "active_branch_id": active_branch_id,
            "recent_messages": recent_messages,
            "maintenance_required": maintenance_required,
            "maintenance_count": maintenance_required.count(),
            "pending_assignments": pending_assignments,
            "pending_assignments_count": pending_assignments.count(),
            "total_income": total_income,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "net_monthly_profit": net_monthly_profit,
            "attendance_days_json": json.dumps(attendance_days),
            "attendance_counts_json": json.dumps(attendance_counts),
            "plan_labels_json": json.dumps(plan_labels),
            "plan_counts_json": json.dumps(plan_counts),
            "monthly_labels_json": json.dumps(monthly_labels),
            "monthly_income_json": json.dumps(monthly_income_data),
            "monthly_expense_json": json.dumps(monthly_expense_data),
        },
    )


@staff_or_trainer_required
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


@staff_or_trainer_required
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
@staff_or_trainer_required
def member_activity_list(request):
    active_branch_id = request.session.get('active_branch_id')
    members = Member.objects.all().select_related('user', 'branch')
    
    if active_branch_id:
        members = members.filter(branch_id=active_branch_id)
        
    activity_data = []
    for m in members:
        last_attn = Attendance.objects.filter(member=m).order_by('-date').first()
        last_pay = Payment.objects.filter(member=m).order_by('-paid_on').first()
        
        activity_data.append({
            'member': m,
            'last_attendance': last_attn,
            'last_payment': last_pay,
            'achievement_count': m.achievements_earned.count(),
            'class_count': m.enrolled_classes.count(),
            'is_active': m.is_currently_active
        })
        
    # Sort by last attendance date descending (members who never checked in go to the bottom)
    from datetime import date
    epoch_date = date(1970, 1, 1)
    
    activity_data.sort(
        key=lambda x: x['last_attendance'].date if (x['last_attendance'] and x['last_attendance'].date) else epoch_date, 
        reverse=True
    )
    
    return render(request, 'gym/admin/member_activity.html', {
        'activity_data': activity_data
    })
