from django.core.management.base import BaseCommand
from django.utils import timezone

from base.gym.models import Membership


class Command(BaseCommand):
    help = "Deactivates memberships whose end_date has passed. Run this daily via a scheduler."

    def handle(self, *args, **options):
        today = timezone.now().date()

        # Bulk-update: one single DB query instead of looping
        expired_qs = Membership.objects.filter(is_active=True, end_date__lt=today)
        count = expired_qs.update(is_active=False)

        if count:
            self.stdout.write(
                self.style.SUCCESS(f"[OK] Expired {count} membership(s) up to {today}.")
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"[OK] No memberships to expire as of {today}."))
