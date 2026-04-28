from django.core.management.base import BaseCommand
from core.services import run_daily_tasks

class Command(BaseCommand):
    help = 'Run all daily automated tasks (payments, overdue checks, notifications)'
    def handle(self, *args, **options):
        run_daily_tasks()
        self.stdout.write(self.style.SUCCESS('Daily tasks completed.'))
