from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


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
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email", "class": "form-control"})
    )
    phone = forms.CharField(
        required=False,
        label="Phone",
        widget=forms.TextInput(attrs={"placeholder": "Enter your phone number", "class": "form-control"})
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a username",
            "email": "Enter your email address",
            "phone": "Enter your phone number",
            "password1": "Create a strong password",
            "password2": "Confirm your password",
        }
        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    "placeholder": placeholder,
                    "class": "form-control"
                })

@login_required
def login_redirect_view(request):
    if request.user.is_staff:
        return redirect("dashboard")
    # Trainers get their own portal
    if hasattr(request.user, "trainer_profile"):
        return redirect("trainer_portal_dashboard")
    # Members get the member portal
    if hasattr(request.user, "member_profile"):
        return redirect("portal_dashboard")
    
    # Fallback for users with no profile/role
    return redirect("home")


from ..models import Member

class StaffCreateForm(forms.Form):
    ROLES = [("admin", "Administrator"), ("trainer", "Trainer")]
    
    role = forms.ChoiceField(choices=ROLES, widget=forms.Select(attrs={"class": "form-control"}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))
    
    # Optional Trainer Fields
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone (for trainers)"}))
    specialization = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Specialization (for trainers)"}))

from ..models import Member, Trainer
from .trainers import admin_required

@admin_required
def staff_create(request):
    if request.method == "POST":
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )
            
            if role == "admin":
                user.is_staff = True
                user.save()
                messages.success(request, f"Admin '{user.username}' created successfully.")
            else:
                # Create Trainer profile
                Trainer.objects.create(
                    user=user,
                    phone=form.cleaned_data["phone"],
                    specialization=form.cleaned_data["specialization"]
                )
                messages.success(request, f"Trainer '{user.username}' created successfully.")
                
            return redirect("dashboard")
    else:
        form = StaffCreateForm()
        
    return render(request, "gym/staff_form.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically create a Member profile for the new user
            Member.objects.create(
                user=user,
                full_name=user.username,
                email=user.email,
                phone=form.cleaned_data.get("phone", "")
            )
            login(request, user)
            return redirect("portal_dashboard")
    else:
        form = RegistrationForm()

    return render(request, "gym/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
