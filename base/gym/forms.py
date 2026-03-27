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
        fields = ["Membership", "amount", "method", "reference"]
        widgets = {
            "method": forms.TextInput(attrs={"placeholder": "e.g., Cash, M-Pesa, Bank"}),
            "reference": forms.TextInput(attrs={"placeholder": "e.g., Transaction ID"}),
        }
        labels = {
            "Membership": "Plan / Membership"
        }

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)
        if member:
            self.fields['Membership'].queryset = Membership.objects.filter(member=member)
        else:
            self.fields['Membership'].queryset = Membership.objects.none()