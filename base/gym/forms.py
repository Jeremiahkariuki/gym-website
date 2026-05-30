from django import forms
from .models import (
    MembershipPlan, Membership, Payment, Member, Expense, 
    MeasurementLog, DietPlan, WorkoutPlan, Exercise,
    GymClass, Equipment, Announcement, GymPhoto, SystemSetting
)

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

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "amount", "category", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

class MeasurementLogForm(forms.ModelForm):
    class Meta:
        model = MeasurementLog
        fields = ["date", "weight", "height", "body_fat"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = ["calories", "protein", "carbs", "fats", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ["name", "start_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["day", "name", "sets", "reps", "order"]


class GymClassForm(forms.ModelForm):
    class Meta:
        model = GymClass
        fields = ["name", "trainer", "day", "start_time", "end_time", "description"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ["name", "category", "purchase_date", "status", "last_maintenance", "description"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "last_maintenance": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "is_active"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5}),
        }

class GymPhotoForm(forms.ModelForm):
    class Meta:
        model = GymPhoto
        fields = ["image", "url", "caption"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = ["gym_name", "contact_email", "phone", "address", "logo_url", "currency_symbol", "opening_hours"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
