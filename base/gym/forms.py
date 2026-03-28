from django import forms
from .models import MembershipPlan, Membership, Payment, Member

class PlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ["name", "price", "duration_days"]


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["plan", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class PaymentForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        label="Plan / Membership",
        required=False,
        empty_label="--- Select a Plan ---"
    )

    class Meta:
        model = Payment
        fields = ["amount", "method", "reference"]
        widgets = {
            "method": forms.TextInput(attrs={"placeholder": "e.g., Cash, M-Pesa, Bank"}),
            "reference": forms.TextInput(attrs={"placeholder": "e.g., Transaction ID"}),
        }

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)