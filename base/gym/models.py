from django.db import models
from django.utils import timezone
from datetime import timedelta

class Member(models.Model):
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    joined_on = models.DateField(auto_now_add=True)

    membership_Plan = models.ForeignKey("MembershipPlan", on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def active_plan_name(self):
        active = self.memberships.filter(is_active=True).first()
        return active.plan.name if active else None

    def __str__(self):
        return self.full_name 
    
class MembershipPlan(models.Model):
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.price}"
    

class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="memberships")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan_id and self.start_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member} - {self.plan}"
    

class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="payments")
    Membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=30, default="Cash")
    reference = models.CharField(max_length=60, blank=True)
    date = models.DateField(default=timezone.now)

    @property
    def plan_name(self):
        if self.Membership and self.Membership.plan:
            return self.Membership.plan.name
        return "N/A"

    @property
    def balance(self):
        if self.Membership and self.Membership.plan:
            # Calculate total amount paid for this specific membership up to this payment
            total_paid = Payment.objects.filter(
                Membership=self.Membership,
                id__lte=self.id
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            return self.Membership.plan.price - total_paid
        return 0

    def __str__(self):
        return f"{self.member} - {self.amount}"
    
class Attedance(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("member", "date")  # one check-in per day

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Utilities", "Utilities"),
        ("Equipment", "Equipment"),
        ("Salary", "Salary"),
        ("Maintenance", "Maintenance"),
        ("Marketing", "Marketing"),
        ("Other", "Other"),
    ]
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

class MeasurementLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="measurements")
    date = models.DateField(default=timezone.now)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm", null=True, blank=True)
    body_fat = models.DecimalField(max_digits=4, decimal_places=1, help_text="Body Fat %", null=True, blank=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=1, editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.weight and self.height:
            height_meters = float(self.height) / 100
            self.bmi = float(self.weight) / (height_meters ** 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.full_name} - {self.date}"

class DietPlan(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="diet_plan")
    calories = models.PositiveIntegerField(help_text="Daily calorie goal")
    protein = models.PositiveIntegerField(help_text="Protein in grams", null=True, blank=True)
    carbs = models.PositiveIntegerField(help_text="Carbs in grams", null=True, blank=True)
    fats = models.PositiveIntegerField(help_text="Fats in grams", null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Diet Plan for {self.member.full_name}"

class WorkoutPlan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="workout_plans")
    name = models.CharField(max_length=100, default="General Workout")
    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.member.full_name}"

class Exercise(models.Model):
    DAYS = [
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"),
        (4, "Friday"), (5, "Saturday"), (6, "Sunday")
    ]
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="exercises")
    day = models.IntegerField(choices=DAYS)
    name = models.CharField(max_length=100)
    sets = models.PositiveIntegerField()
    reps = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["day", "order"]

    def __str__(self):
        return f"{self.name} on {self.get_day_display()}"



