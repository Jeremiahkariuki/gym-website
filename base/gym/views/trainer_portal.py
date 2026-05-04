from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from ..models import Trainer, Attedance, Membership


def trainer_required(view_func):
    """Only allow users who have a Trainer profile."""
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            request.trainer = request.user.trainer_profile
        except Trainer.DoesNotExist:
            return redirect("login_redirect")
        return view_func(request, *args, **kwargs)
    return wrapper


@trainer_required
def trainer_portal_dashboard(request):
    trainer = request.trainer
    today = timezone.now().date()
    seven_days = today + timedelta(days=7)

    # Members assigned to this trainer
    assignments = trainer.assignments.select_related("member").order_by("member__full_name")
    member_ids = assignments.values_list("member_id", flat=True)

    # Today's attendance for their members
    today_checkins = Attedance.objects.filter(
        member_id__in=member_ids, date=today
    ).select_related("member").count()

    # Expiring memberships (among their members)
    expiring_soon = Membership.objects.filter(
        member_id__in=member_ids,
        is_active=True,
        end_date__isnull=False,
        end_date__gte=today,
        end_date__lte=seven_days,
    ).select_related("member", "plan").order_by("end_date")

    return render(request, "gym/trainer_portal/dashboard.html", {
        "trainer": trainer,
        "assignments": assignments,
        "today_checkins": today_checkins,
        "expiring_soon": expiring_soon,
        "today": today,
    })


@trainer_required
def trainer_portal_members(request):
    trainer = request.trainer
    assignments = trainer.assignments.select_related(
        "member__trainer_assignment__trainer__user"
    ).prefetch_related("member__memberships__plan").order_by("member__full_name")
    return render(request, "gym/trainer_portal/members.html", {
        "trainer": trainer,
        "assignments": assignments,
    })
