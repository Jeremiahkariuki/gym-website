from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    manager_name = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Member(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="members", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member_profile", null=True, blank=True)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    joined_on = models.DateField(auto_now_add=True)
    checkin_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    membership_Plan = models.ForeignKey("MembershipPlan", on_delete=models.SET_NULL, null=True, blank=True)
    
    # Profile Hub Fields
    GOAL_CHOICES = [
        ("Weight Loss", "Weight Loss"),
        ("Muscle Gain", "Muscle Gain"),
        ("Endurance", "Endurance"),
        ("Flexibility", "Flexibility"),
        ("General Fitness", "General Fitness"),
    ]
    fitness_goal = models.CharField(max_length=50, choices=GOAL_CHOICES, default="General Fitness")
    medical_conditions = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, help_text="Upload profile image")

    @property
    def active_plan_name(self):
        active = self.active_membership
        return active.plan.name if active else None

    @property
    def active_membership(self):
        """Returns the current valid membership if one exists."""
        return self.memberships.filter(is_active=True).first()
    
    @property
    def is_currently_active(self):
        """Checks if the member has a valid, non-expired membership."""
        active = self.active_membership
        if active and not active.is_expired:
            return True
        return False

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
    is_active = models.BooleanField(default=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan_id and self.start_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Returns True if the membership end date has passed."""
        if self.end_date:
            return self.end_date < timezone.now().date()
        return False

    def __str__(self):
        return f"{self.member} - {self.plan}"
    

class Payment(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="payments")
    Membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(default=timezone.now, db_index=True)
    method = models.CharField(max_length=30, default="Cash")
    reference = models.CharField(max_length=60, blank=True)
    date = models.DateField(default=timezone.now, db_index=True)

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
    
class Attendance(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="attendance_records", null=True, blank=True)
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, db_index=True)  # DateField so unique_together works per day

    class Meta:
        unique_together = ("member", "date")  # one check-in per day

class Expense(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="expenses", null=True, blank=True)
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


class Trainer(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="trainers", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trainer_profile")
    phone = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. Weight Loss, Bodybuilding, Yoga"
    )
    bio = models.TextField(blank=True)
    joined_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def assigned_members_count(self):
        return self.assignments.count()


class TrainerAssignment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="assignments", null=True, blank=True)
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="trainer_assignment")
    assigned_on = models.DateField(auto_now_add=True)
    requested_on = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.trainer} → {self.member}"


class GymClass(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="classes", null=True, blank=True)
    DAYS = [
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"),
        (4, "Friday"), (5, "Saturday"), (6, "Sunday")
    ]
    name = models.CharField(max_length=100)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name="classes")
    day = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField(blank=True)
    members = models.ManyToManyField(Member, related_name="enrolled_classes", blank=True)

    class Meta:
        verbose_name_plural = "Gym Classes"
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.name} ({self.get_day_display()})"


class Equipment(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="equipment", null=True, blank=True)
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Maintenance", "Maintenance"),
        ("Retired", "Retired"),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    last_maintenance = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Equipment"

    def __str__(self):
        return self.name


class Announcement(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="announcements", null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title


class GymPhoto(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="photos", null=True, blank=True)
    url = models.URLField(max_length=500, help_text="Direct link to the gym image")
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Photo {self.id}"


class SystemSetting(models.Model):
    gym_name = models.CharField(max_length=100, default="Antigravity Gym")
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    currency_symbol = models.CharField(max_length=5, default="$")
    opening_hours = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "System Setting"

    def __str__(self):
        return "Gym Settings"

    def save(self, *args, **kwargs):
        if not self.pk and SystemSetting.objects.exists():
            return
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg from {self.name} - {self.subject}"

# --- New Member Features ---

class LibraryExercise(models.Model):
    CATEGORY_CHOICES = [
        ("Strength", "Strength"),
        ("Cardio", "Cardio"),
        ("Flexibility", "Flexibility"),
        ("HIIT", "HIIT"),
        ("Other", "Other"),
    ]
    DIFFICULTY_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    instructions = models.TextField(help_text="Step-by-step instructions")
    video_url = models.URLField(blank=True, null=True, help_text="Link to exercise video")
    thumbnail_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class ProgressPhoto(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="progress_photos")
    date = models.DateField(default=timezone.now)
    photo_before = models.URLField(help_text="URL to 'before' or current progress photo")
    photo_after = models.URLField(blank=True, null=True, help_text="URL to 'after' photo (optional)")
    weight_at_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Progress for {self.member.full_name} on {self.date}"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_emoji = models.CharField(max_length=10, default="🏆")
    requirement_description = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class MemberAchievement(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="achievements_earned")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("member", "achievement")

    def __str__(self):
        return f"{self.member.full_name} - {self.achievement.name}"
