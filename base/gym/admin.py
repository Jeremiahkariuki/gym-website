from django.contrib import admin
from .models import Member, Membership, MembershipPlan, Payment, Attedance, Expense, MeasurementLog, DietPlan, WorkoutPlan, Exercise, Trainer, TrainerAssignment, GymClass, ContactMessage


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'start_time', 'end_time', 'trainer')
    list_filter = ('day', 'trainer')
    search_fields = ('name',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('name', 'email', 'subject')
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'joined_on', 'membership_Plan')
    list_filter = ('joined_on', 'membership_Plan')
    search_fields = ('full_name', 'phone', 'email')
    readonly_fields = ('joined_on',)


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')
    list_filter = ('duration_days',)
    search_fields = ('name',)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'plan')
    search_fields = ('member__full_name',)
    readonly_fields = ('end_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'paid_on', 'method', 'reference')
    list_filter = ('paid_on', 'method')
    search_fields = ('member__full_name', 'reference')
    readonly_fields = ('paid_on',)


@admin.register(Attedance)
class AttedanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'date')
    list_filter = ('date',)
    search_fields = ('member__full_name',)
    readonly_fields = ('date',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'date')
    list_filter = ('category', 'date')

@admin.register(MeasurementLog)
class MeasurementLogAdmin(admin.ModelAdmin):
    list_display = ('member', 'date', 'weight', 'body_fat', 'bmi')
    list_filter = ('date',)

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ('member', 'calories', 'protein', 'carbs', 'fats')

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'member', 'start_date', 'is_active')
    list_filter = ('is_active', 'start_date')

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'workout_plan', 'day', 'order')
    list_filter = ('day',)


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'specialization', 'phone', 'joined_on')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')
    readonly_fields = ('joined_on',)


@admin.register(TrainerAssignment)
class TrainerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'member', 'assigned_on')
    list_filter = ('trainer',)
    search_fields = ('trainer__user__username', 'member__full_name')
    readonly_fields = ('assigned_on',)
