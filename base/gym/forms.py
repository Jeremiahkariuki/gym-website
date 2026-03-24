from django import forms
from .models import MembershipPlan, Membership, Payment, Member

class PlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ["name", "price", "duration_days"]


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["member", "plan", "start_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "Membership", "amount", "method", "reference"]
        widgets = {
            "method": forms.TextInput(attrs={"placeholder": "e.g., Cash, M-Pesa, Bank"}),
            "reference": forms.TextInput(attrs={"placeholder": "e.g., Transaction ID"}),
        }