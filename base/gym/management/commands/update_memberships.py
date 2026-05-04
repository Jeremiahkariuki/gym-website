import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from base.gym.models import Membership

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Updates membership statuses, marking them inactive if their end dates have passed."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Find all active memberships whose end date has passed
        expired_memberships = Membership.objects.filter(
            is_active=True,
            end_date__lt=today
        )

        count = expired_memberships.count()
        
        if count > 0:
            self.stdout.write(self.style.WARNING(f"Found {count} expired memberships. Updating..."))
            
            # Bulk update for performance
            expired_memberships.update(is_active=False)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully marked {count} memberships as inactive."))
            logger.info(f"Automatically marked {count} memberships as inactive.")
        else:
            self.stdout.write(self.style.SUCCESS("No active expired memberships found. Everything is up to date."))
