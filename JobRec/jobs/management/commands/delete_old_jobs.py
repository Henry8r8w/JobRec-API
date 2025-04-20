
from django.core.management.base import BaseCommand
from jobs.models import JobPost
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete job posts older than 30 days'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=30)
        deleted, _ = JobPost.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f"Deleted {deleted} old job posts.") # help - info std output display
