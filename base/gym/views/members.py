import csv

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models as db_models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..decorators import admin_required, staff_or_trainer_required

from ..models import (
    DietPlan,
    Member,
    Membership,
    MembershipPlan,
    Payment,
)


class MemberForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        label="Membership Plan",
        required=True,
        empty_label="--- Select a Plan ---",
        help_text="A starting membership plan is required for all new members.",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Member
        fields = ["full_name", "phone", "email", "address"]


@admin_required
def member_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    active_branch_id = request.session.get('active_branch_id')
    qs = (
        Member.objects.select_related("diet_plan")
        .prefetch_related("memberships__plan")
        .order_by("-joined_on")
    )

    if active_branch_id:
        qs = qs.filter(branch_id=active_branch_id)

    if query:
        qs = qs.filter(
            db_models.Q(full_name__icontains=query) | db_models.Q(phone__icontains=query)
        )
        
    if status == "active":
        qs = qs.filter(memberships__is_active=True).distinct()
    elif status == "inactive":
        # Members with no active membership
        qs = qs.exclude(memberships__is_active=True).distinct()

    paginator = Paginator(qs, 25)  # 25 members per page
    page_number = request.GET.get("page")
    members = paginator.get_page(page_number)

    return render(request, "gym/member_list.html", {"members": members, "query": query, "status": status})


@admin_required
def member_create(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            active_branch_id = request.session.get('active_branch_id')
            member = form.save(commit=False)
            if active_branch_id:
                member.branch_id = active_branch_id
            member.save()
            
            plan = form.cleaned_data.get("plan")
            if plan:
                Membership.objects.create(
                    member=member,
                    plan=plan,
                    is_active=True,
                    start_date=timezone.now(),
                )
            messages.success(request, "Member added successfully.")
            return redirect("member_list")
    else:
        form = MemberForm()
    return render(request, "gym/member_form.html", {"form": form})


@admin_required
def member_edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    active_membership = member.memberships.filter(is_active=True).first()

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            plan = form.cleaned_data.get("plan")

            if plan:
                if not active_membership or active_membership.plan != plan:
                    if active_membership:
                        active_membership.is_active = False
                        active_membership.save()
                    Membership.objects.create(
                        member=member,
                        plan=plan,
                        is_active=True,
                        start_date=timezone.now(),
                    )
            elif active_membership and not plan:
                active_membership.is_active = False
                active_membership.save()

            messages.success(request, "Member updated successfully.")
            return redirect("member_list")
    else:
        initial_data = {}
        if active_membership:
            initial_data["plan"] = active_membership.plan
        form = MemberForm(instance=member, initial=initial_data)

    return render(request, "gym/member_form.html", {"form": form, "member": member})


@admin_required
def member_delete(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        member.delete()
        return redirect("member_list")
    return render(request, "gym/member_confirm_delete.html", {"member": member})


@login_required
def member_detail(request, member_id):
    member = get_object_or_404(Member, id=member_id)

    # Allow access only to: admins, trainers, or the member viewing their own profile
    is_admin = request.user.is_staff
    is_trainer = hasattr(request.user, 'trainer_profile')
    is_self = hasattr(request.user, 'member_profile') and request.user.member_profile.id == member.id
    if not (is_admin or is_trainer or is_self):
        messages.error(request, "You don't have permission to view this profile.")
        return redirect("portal_dashboard")
    memberships = member.memberships.all()
    payments = member.payments.all()
    attendance = member.attendance_set.all().order_by("-date")[:30]

    measurements = member.measurements.all().order_by("-date")
    try:
        diet_plan = member.diet_plan
    except DietPlan.DoesNotExist:
        diet_plan = None
    workout_plans = member.workout_plans.all()

    return render(
        request,
        "gym/member_detail.html",
        {
            "member": member,
            "memberships": memberships,
            "payments": payments,
            "attendance": attendance,
            "measurements": measurements,
            "diet_plan": diet_plan,
            "workout_plans": workout_plans,
        },
    )


@admin_required
def export_members_csv(request):
    """Download all members as a CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="members.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Phone", "Email", "Address", "Joined On", "Active Plan"])

    active_branch_id = request.session.get('active_branch_id')
    qs = Member.objects.prefetch_related("memberships__plan").order_by("full_name")
    
    if active_branch_id:
        qs = qs.filter(branch_id=active_branch_id)

    for member in qs:
        active = member.memberships.filter(is_active=True).first()
        writer.writerow([
            member.full_name,
            member.phone,
            member.email or "",
            member.address or "",
            member.joined_on,
            active.plan.name if active else "None",
        ])

    return response

@admin_required
def import_members_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "This is not a CSV file.")
            return redirect("import_members_csv")
            
        try:
            file_data = csv_file.read().decode("utf-8")
            lines = file_data.split("\n")
            
            # Skip header, iterate through rows
            created_count = 0
            for line in lines[1:]:
                fields = line.split(",")
                if len(fields) >= 2 and fields[0].strip():
                    full_name = fields[0].strip()
                    phone = fields[1].strip() if len(fields) > 1 else ""
                    email = fields[2].strip() if len(fields) > 2 else ""
                    address = fields[3].strip() if len(fields) > 3 else ""
                    
                    active_branch_id = request.session.get('active_branch_id')
                    Member.objects.get_or_create(
                        phone=phone,
                        defaults={
                            "full_name": full_name,
                            "email": email,
                            "address": address,
                            "branch_id": active_branch_id
                        }
                    )
                    created_count += 1
            
            messages.success(request, f"Successfully imported {created_count} members.")
            return redirect("member_list")
        except Exception as e:
            messages.error(request, f"Unable to upload file. Error: {e}")
            return redirect("import_members_csv")

    return render(request, "gym/import_members.html")
