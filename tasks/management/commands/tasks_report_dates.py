from datetime import datetime, timezone

from django.core.management import BaseCommand

from tasks.models import TodoItem


class Command(BaseCommand):
    help = u"Dump all task dates"

    def add_arguments(self, parser):
        parser.add_argument(
            '--warning-days', dest='warn_days', type=int, default=5)

    def handle(self, *args, **options):
        now = datetime.now(timezone.utc)
        for t in TodoItem.objects.filter(is_completed=False):
            timestamp = t.created.replace(tzinfo=None)
            if (now - t.created).days >= options['warn_days']:
                print("Старая задача:", t, t.created)
