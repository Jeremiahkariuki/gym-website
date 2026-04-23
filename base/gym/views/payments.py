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
