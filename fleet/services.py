from django.utils import timezone
from datetime import date
from .models import Contract

def auto_expire_contracts(today=None):
    today = today or date.today()
    for c in Contract.objects.filter(status='active', end_date__lt=today):
        c.status = 'expired'
        c.save()