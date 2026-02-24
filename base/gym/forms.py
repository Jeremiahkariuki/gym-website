from django import forms
from .models import MembershipPlan

class PlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ["name", "price", "duration_days"]