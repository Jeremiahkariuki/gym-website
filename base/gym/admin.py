from django.contrib import admin
from .models import Member, Membership, MembershipPlan, Payment, Attedance


@admin.register(Member)
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
