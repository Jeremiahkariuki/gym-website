from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.db import transaction, IntegrityError


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


@login_required
def login_redirect_view(request):
    from django.urls import reverse
    # Check if there is a 'next' parameter in the URL
    next_url = request.GET.get('next')
    if next_url and next_url != reverse('login_redirect') and next_url != '/':
        return redirect(next_url)

    # Admins get the main management dashboard
    if request.user.is_staff:
        return redirect("dashboard")
    
    # Trainers get their own portal
    if getattr(request.user, "trainer_profile", None):
        return redirect("trainer_portal_dashboard")
        
    # Members get the member portal
    if getattr(request.user, "member_profile", None):
        return redirect("portal_dashboard")
    
    # Fallback for users with no profile/role
    # If we are already at / and redirecting to / it might cause issues
    # but since this is usually called after login, it should be fine.
    return render(request, "gym/home.html", {"is_authenticated": True})


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

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone = phone.strip()
            if Member.objects.filter(phone=phone).exists():
                raise forms.ValidationError("This phone number is already registered.")
        return phone




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

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and Member.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered to a member.")
        if phone and Trainer.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered to a trainer.")
        return phone

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
                phone=form.cleaned_data.get("phone") or None,
                    specialization=form.cleaned_data["specialization"]
                )
                messages.success(request, f"Trainer '{user.username}' created successfully.")
                
            return redirect("dashboard")
    else:
        form = StaffCreateForm()
        
    return render(request, "gym/staff_form.html", {"form": form})


def register_view(request):
    next_url = request.GET.get('next', '')
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    # Automatically create a Member profile for the new user
                    Member.objects.create(
                        user=user,
                        full_name=user.username,
                        email=user.email,
                        phone=form.cleaned_data.get("phone") or None
                    )
                messages.success(request, "Account created successfully! Please login to continue.")
                login_url = redirect("login").url
                if next_url:
                    return redirect(f"{login_url}?next={next_url}")
                return redirect("login")
            except IntegrityError:
                form.add_error("phone", "This phone number is already in use.")
    else:
        form = RegistrationForm()

    return render(request, "gym/register.html", {"form": form})


def logout_view(request):
    logout(request)
    next_page = request.GET.get('next', 'home')
    return redirect(next_page)
