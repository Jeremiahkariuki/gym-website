import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import ExpenseForm, PaymentForm
from ..models import Expense, Member, Membership, Payment


@login_required
def record_payment(request, member_id):
    member = get_object_or_404(Member, id=member_id)

    if request.method == "POST":
        form = PaymentForm(request.POST, member=member)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.member = member

            plan = form.cleaned_data.get("plan")
            if plan:
                membership, _ = Membership.objects.get_or_create(
                    member=member,
                    plan=plan,
                    is_active=True,
                    defaults={"start_date": timezone.now()},
                )
                payment.Membership = membership

            payment.save()
            messages.success(request, "Payment recorded successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        form = PaymentForm(member=member)

    return render(request, "gym/payment_form.html", {"form": form, "member": member})


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    member = payment.member
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            plan = form.cleaned_data.get("plan")
            if plan:
                membership, _ = Membership.objects.get_or_create(
                    member=member,
                    plan=plan,
                    is_active=True,
                    defaults={"start_date": timezone.now()},
                )
                payment.Membership = membership
            payment.save()
            messages.success(request, "Payment updated successfully.")
            return redirect("member_detail", member_id=member.id)
    else:
        initial_data = {}
        if payment.Membership and payment.Membership.plan:
            initial_data["plan"] = payment.Membership.plan.id
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
    return render(
        request,
        "gym/payment_confirm_delete.html",
        {"payment": payment, "member": member},
    )


# ── Expenses ────────────────────────────────────────────────────────────── #

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


# ── Revenue Report ───────────────────────────────────────────────────────── #

@login_required
def revenue_report(request):
    today = timezone.now().date()
    this_month = today.replace(day=1)

    total_revenue = Payment.objects.aggregate(total=db_models.Sum("amount"))["total"] or 0
    monthly_revenue = (
        Payment.objects.filter(date__year=today.year, date__month=today.month)
        .aggregate(total=db_models.Sum("amount"))["total"] or 0
    )

    total_expenses = Expense.objects.aggregate(total=db_models.Sum("amount"))["total"] or 0
    monthly_expenses = (
        Expense.objects.filter(date__year=today.year, date__month=today.month)
        .aggregate(total=db_models.Sum("amount"))["total"] or 0
    )

    payment_methods = Payment.objects.values("method").annotate(
        total=db_models.Sum("amount"),
        count=db_models.Count("id"),
    )

    members = Member.objects.all().prefetch_related("payments", "memberships__plan")
    member_status = []
    for member in members:
        has_paid = member.payments.filter(
            date__year=today.year, date__month=today.month
        ).exists()
        active_membership = member.memberships.filter(is_active=True).first()
        plan_name = active_membership.plan.name if active_membership else "No Active Plan"
        member_status.append(
            {"member": member, "has_paid": has_paid, "plan_name": plan_name}
        )

    # --- Data for Financial Dashboard Charts ---
    six_months_ago = today - timedelta(days=180)
    
    # 1. Monthly Revenue vs Expenses Trend (Last 6 Months)
    from django.db.models.functions import TruncMonth
    
    monthly_trends_raw = Payment.objects.filter(date__gte=six_months_ago)\
        .annotate(month=TruncMonth('date'))\
        .values('month')\
        .annotate(revenue=db_models.Sum('amount'))\
        .order_by('month')

    expense_trends_raw = Expense.objects.filter(date__gte=six_months_ago)\
        .annotate(month=TruncMonth('date'))\
        .values('month')\
        .annotate(expenses=db_models.Sum('amount'))\
        .order_by('month')

    # Merge trends into a combined list for the chart
    trend_data = {}
    for entry in monthly_trends_raw:
        m_str = entry['month'].strftime("%b %Y")
        trend_data[m_str] = {'revenue': float(entry['revenue'] or 0), 'expenses': 0}
    
    for entry in expense_trends_raw:
        m_str = entry['month'].strftime("%b %Y")
        if m_str not in trend_data:
            trend_data[m_str] = {'revenue': 0, 'expenses': 0}
        trend_data[m_str]['expenses'] = float(entry['expenses'] or 0)
    
    # Sort trend_data by date (the keys are strings, so we might need a better sort if they span years)
    sorted_months = sorted(trend_data.keys(), key=lambda x: timezone.datetime.strptime(x, "%b %Y"))
    chart_labels = sorted_months
    chart_revenue = [trend_data[m]['revenue'] for m in sorted_months]
    chart_expenses = [trend_data[m]['expenses'] for m in sorted_months]

    # 2. Revenue by Membership Plan
    revenue_by_plan = Payment.objects.filter(Membership__isnull=False)\
        .values('Membership__plan__name')\
        .annotate(total=db_models.Sum('amount'))\
        .order_by('-total')
    
    plan_labels = [entry['Membership__plan__name'] for entry in revenue_by_plan]
    plan_data = [float(entry['total'] or 0) for entry in revenue_by_plan]

    # 3. Expenses by Category
    expenses_by_category = Expense.objects.values('category')\
        .annotate(total=db_models.Sum('amount'))\
        .order_by('-total')
    
    category_labels = [entry['category'] for entry in expenses_by_category]
    category_data = [float(entry['total'] or 0) for entry in expenses_by_category]

    return render(
        request,
        "gym/revenue_report.html",
        {
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "total_expenses": total_expenses,
            "monthly_expenses": monthly_expenses,
            "monthly_profit": monthly_revenue - monthly_expenses,
            "total_profit": total_revenue - total_expenses,
            "payment_methods": payment_methods,
            "month": this_month.strftime("%B %Y"),
            "member_status": member_status,
            # Chart Data
            "chart_labels": chart_labels,
            "chart_revenue": chart_revenue,
            "chart_expenses": chart_expenses,
            "plan_labels": plan_labels,
            "plan_data": plan_data,
            "category_labels": category_labels,
            "category_data": category_data,
        },
    )


@login_required
def export_payments_csv(request):
    """Download all payments as a CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    writer.writerow(["Member", "Amount", "Method", "Plan", "Date", "Reference"])

    for p in Payment.objects.select_related("member", "Membership__plan").order_by("-date"):
        writer.writerow([
            p.member.full_name,
            p.amount,
            p.method,
            p.plan_name,
            p.date,
            p.reference or "",
        ])

    return response
