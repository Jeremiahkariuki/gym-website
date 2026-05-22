from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from ..decorators import admin_required, staff_or_trainer_required

from ..forms import MembershipForm, PlanForm
from ..models import Member, Membership, MembershipPlan


@staff_or_trainer_required
def plan_list(request):
    plans = MembershipPlan.objects.all().order_by("price")
    return render(request, "gym/plan_list.html", {"plans": plans})


@admin_required
def plan_create(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership Plan created successfully.")
            return redirect("plan_list")
    else:
        form = PlanForm()
    return render(request, "gym/plan_form.html", {"form": form})


@admin_required
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


@admin_required
def plan_delete(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Membership Plan deleted successfully.")
        return redirect("plan_list")
    return render(request, "gym/plan_confirm_delete.html", {"plan": plan})


@admin_required
def assign_membership(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    active_membership = member.memberships.filter(is_active=True).first()

    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            # Deactivate any existing active membership
            if active_membership:
                active_membership.is_active = False
                active_membership.save()

            membership = form.save(commit=False)
            membership.member = member
            membership.is_active = True
            membership.save()

            # Update the member's assigned plan
            member.membership_Plan = membership.plan
            member.save()

            messages.success(
                request,
                f"Membership '{membership.plan.name}' assigned to {member.full_name} successfully."
            )
            return redirect("member_detail", member_id=member.id)
    else:
        form = MembershipForm(initial={"member": member})

    plans = MembershipPlan.objects.all().order_by("price")
    return render(request, "gym/membership_form.html", {
        "form": form,
        "member": member,
        "active_membership": active_membership,
        "plans": plans,
    })


@admin_required
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    member = membership.member
    next_url = (
        request.POST.get("next_url")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER", "")
    )

    if request.method == "POST":
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership updated successfully.")
            return redirect(next_url) if next_url else redirect("member_detail", member_id=member.id)
    else:
        form = MembershipForm(instance=membership)

    return render(
        request,
        "gym/membership_form.html",
        {"form": form, "member": member, "next_url": next_url},
    )


@admin_required
def membership_delete(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    member = membership.member
    if request.method == "POST":
        membership.delete()
        messages.success(request, "Membership deleted successfully.")
        return redirect("member_detail", member_id=member.id)
    return render(
        request,
        "gym/membership_confirm_delete.html",
        {"membership": membership, "member": member},
    )
