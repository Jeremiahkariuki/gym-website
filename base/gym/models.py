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

