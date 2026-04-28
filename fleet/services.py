from django.utils import timezone
from datetime import date
from .models import Contract, Payment

def auto_expire_contracts(today=None):
    today = today or date.today()
    for c in Contract.objects.filter(status='active', end_date__lt=today):
        c.status = 'expired'
        c.save()

def run_daily_tasks():
    today = date.today()
    auto_expire_contracts(today)
    mark_overdue_payments()
    generate_daily_payments()

def mark_overdue_payments(today=None):
    today = today or date.today()
    Payment.objects.filter(due_date__lt=today, status__in=['pending','partial']).update(status='overdue')


def generate_daily_payments(today=None):
    today = today or date.today()
    active = Contract.objects.filter(status='active', start_date__lte=today, end_date__gte=today)
    for contract in active:
        Payment.objects.get_or_create(
            contract=contract, due_date=today,
            defaults={'amount': contract.daily_rate, 'balance': contract.daily_rate, 'status': 'pending'}
        )
