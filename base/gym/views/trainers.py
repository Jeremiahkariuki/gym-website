from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models as db_models
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Member, Trainer, TrainerAssignment


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------

class TrainerCreateForm(forms.Form):
    """Combines User creation fields with Trainer-specific fields."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
    )
    specialization = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Weight Loss, Yoga"}),
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short bio…"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username


class TrainerEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Trainer
        fields = ["phone", "specialization", "bio"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "specialization": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        trainer = super().save(commit=False)
        trainer.user.first_name = self.cleaned_data["first_name"]
        trainer.user.last_name = self.cleaned_data["last_name"]
        trainer.user.email = self.cleaned_data["email"]
        trainer.user.save()
        if commit:
            trainer.save()
        return trainer


class AssignTrainerForm(forms.Form):
    trainer = forms.ModelChoiceField(
        queryset=Trainer.objects.select_related("user").all(),
        required=False,
        empty_label="--- Remove trainer ---",
        widget=forms.Select(attrs={"class": "form-control"}),
    )


# ---------------------------------------------------------------------------
# Helper decorator
# ---------------------------------------------------------------------------

def admin_required(view_func):
    """
    Only allow is_staff users.
    Redirects unauthenticated users to the custom login page.
    Redirects authenticated non-staff users to their dashboard-redirect.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_staff:
            return redirect("login_redirect")
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@admin_required
def trainer_list(request):
    active_branch_id = request.session.get('active_branch_id')
    query = request.GET.get("q", "").strip()
    qs = Trainer.objects.select_related("user").annotate(
        member_count=db_models.Count("assignments")
    ).order_by("user__first_name", "user__username")
    
    if active_branch_id:
        qs = qs.filter(branch_id=active_branch_id)

    if query:
        qs = qs.filter(
            db_models.Q(user__first_name__icontains=query)
            | db_models.Q(user__last_name__icontains=query)
            | db_models.Q(user__username__icontains=query)
            | db_models.Q(specialization__icontains=query)
        )

    paginator = Paginator(qs, 20)
    trainers = paginator.get_page(request.GET.get("page"))
    return render(request, "gym/trainer_list.html", {"trainers": trainers, "query": query})


@admin_required
def trainer_create(request):
    if request.method == "POST":
        form = TrainerCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
            )
            active_branch_id = request.session.get('active_branch_id')
            Trainer.objects.create(
                user=user,
                phone=form.cleaned_data.get("phone") or None,
                specialization=form.cleaned_data["specialization"],
                bio=form.cleaned_data["bio"],
                branch_id=active_branch_id,
            )
            messages.success(request, f"Trainer '{user.username}' created successfully.")
            return redirect("trainer_list")
    else:
        form = TrainerCreateForm()
    return render(request, "gym/trainer_form.html", {"form": form, "title": "Add Trainer"})


@admin_required
def trainer_detail(request, trainer_id):
    trainer = get_object_or_404(Trainer.objects.select_related("user"), id=trainer_id)
    assignments = trainer.assignments.select_related("member").order_by("member__full_name")
    return render(request, "gym/trainer_detail.html", {
        "trainer": trainer,
        "assignments": assignments,
    })


@admin_required
def trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer.objects.select_related("user"), id=trainer_id)
    if request.method == "POST":
        form = TrainerEditForm(request.POST, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer updated successfully.")
            return redirect("trainer_detail", trainer_id=trainer.id)
    else:
        form = TrainerEditForm(instance=trainer)
    return render(request, "gym/trainer_form.html", {"form": form, "trainer": trainer, "title": "Edit Trainer"})


@admin_required
def trainer_delete(request, trainer_id):
    trainer = get_object_or_404(Trainer.objects.select_related("user"), id=trainer_id)
    if request.method == "POST":
        trainer.user.delete()  # cascades to Trainer record
        messages.success(request, "Trainer deleted.")
        return redirect("trainer_list")
    return render(request, "gym/trainer_confirm_delete.html", {"trainer": trainer})


@admin_required
def assign_trainer(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    current_assignment = getattr(member, "trainer_assignment", None)

    if request.method == "POST":
        form = AssignTrainerForm(request.POST)
        if form.is_valid():
            selected_trainer = form.cleaned_data["trainer"]
            direct_assign = request.POST.get("direct_assign") == "on"
            status = "accepted" if direct_assign else "pending"
            
            if current_assignment:
                if selected_trainer:
                    current_assignment.trainer = selected_trainer
                    current_assignment.status = status
                    current_assignment.save()
                    msg = f"Trainer updated to {selected_trainer}."
                    if not direct_assign:
                        msg += " (Pending Trainer Approval)"
                    messages.success(request, msg)
                else:
                    current_assignment.delete()
                    messages.success(request, "Trainer removed.")
            elif selected_trainer:
                TrainerAssignment.objects.create(
                    trainer=selected_trainer, 
                    member=member,
                    status=status
                )
                msg = f"{selected_trainer} assigned to {member}."
                if not direct_assign:
                    msg += " (Pending Trainer Approval)"
                messages.success(request, msg)
            return redirect("member_detail", member_id=member.id)
    else:
        initial = {"trainer": current_assignment.trainer if current_assignment else None}
        form = AssignTrainerForm(initial=initial)

    return render(request, "gym/assign_trainer_form.html", {
        "form": form,
        "member": member,
        "current_assignment": current_assignment,
    })

@login_required
def trainer_assignment_list(request):
    """View for trainers to see pending member assignments."""
    try:
        trainer = request.user.trainer_profile
    except Trainer.DoesNotExist:
        messages.error(request, "Only trainers can access this page.")
        return redirect("home")
        
    pending_assignments = trainer.assignments.filter(status="pending").select_related("member")
    accepted_assignments = trainer.assignments.filter(status="accepted").select_related("member")
    
    return render(request, "gym/trainer_portal/assignments.html", {
        "pending": pending_assignments,
        "accepted": accepted_assignments,
    })

@login_required
def trainer_assignment_action(request, assignment_id, action):
    """Action for trainers to accept or reject assignments."""
    assignment = get_object_or_404(TrainerAssignment, id=assignment_id)
    
    # Check if user is the assigned trainer OR an admin (for override)
    is_trainer = hasattr(request.user, 'trainer_profile') and assignment.trainer == request.user.trainer_profile
    is_admin = request.user.is_staff
    
    if not (is_trainer or is_admin):
        messages.error(request, "Unauthorized.")
        return redirect("login_redirect")
        
    if action == "accept":
        assignment.status = "accepted"
        assignment.save()
        messages.success(request, f"Assignment for {assignment.member.full_name} accepted.")
    elif action == "reject":
        assignment.status = "rejected"
        assignment.save()
        messages.warning(request, f"Assignment for {assignment.member.full_name} rejected.")
        
    if is_admin:
        return redirect("member_detail", member_id=assignment.member.id)
    return redirect("trainer_assignment_list")
