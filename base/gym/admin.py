from django.contrib import admin
from .models import Member, Membership, MembershipPlan, Payment

admin.site.register(Member)
admin.site.register(MembershipPlan)
admin.site.register(Membership)
admin.site.register(Payment)
