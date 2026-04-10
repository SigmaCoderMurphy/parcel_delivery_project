from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from leads.models import CallLog, CommunicationLog, FollowUp, Lead, Quote, ScheduledEmail


class Command(BaseCommand):
    help = (
        "Delete ALL users and ALL lead-related operational data "
        "(leads, quotes, followups, communication logs, call logs, scheduled emails). "
        "Keeps services/testimonials/site settings untouched."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required safety flag. Without this flag nothing is deleted.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what will be deleted without changing the database.",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError("Refusing to run. Use --confirm to execute deletion.")

        User = get_user_model()
        total_users = User.objects.count()
        total_leads = Lead.objects.count()
        dependent_counts = {
            "quotes": Quote.objects.count(),
            "followups": FollowUp.objects.count(),
            "communications": CommunicationLog.objects.count(),
            "scheduled_emails": ScheduledEmail.objects.count(),
            "calls": CallLog.objects.count(),
        }

        self.stdout.write(self.style.WARNING("About to purge operational data:"))
        self.stdout.write(f"- Users: {total_users}")
        self.stdout.write(f"- Leads: {total_leads}")
        for name, count in dependent_counts.items():
            self.stdout.write(f"- {name}: {count}")

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("Dry run complete. No rows deleted."))
            return

        with transaction.atomic():
            # Delete lead tree first (cascades to quotes/followups/communications/scheduled emails/call analysis)
            Lead.objects.all().delete()
            # Delete all users last to avoid FK set-null overhead on large lead trees.
            User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Operational data purge complete."))
