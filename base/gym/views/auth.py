from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
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
    return redirect("portal_dashboard")


from ..models import Member

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        return redirect("portal_dashboard")

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
