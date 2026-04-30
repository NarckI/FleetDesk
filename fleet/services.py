from django.utils import timezone
from datetime import date
from .models import Contract, Payment, Driver, Vehicle, Notification

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
    generate_notifications()

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

def generate_notifications(today=None):
    today = today or date.today()

    for driver in Driver.objects.filter(status='active'):
        days_left = (driver.license_expiry - today).days
        if days_left == 21 or 0 <= days_left <= 14:
            sev = 'high' if 0 <= days_left <= 7 else 'medium'
            Notification.objects.get_or_create(
                notification_type='license_expiry', related_driver=driver,
                created_at__date=today,
                defaults={
                    'title': 'Driver License Expiring Soon',
                    'message': f"{driver.full_name}'s license expires in {days_left} days ({driver.license_expiry}).",
                    'severity': sev, 'related_driver': driver,
                }
            )

    for vehicle in Vehicle.objects.all():
        for field, ntype, label in [
            ('or_expiry','or_expiry','OR'),
            ('cr_expiry','cr_expiry','CR'),
            ('cpc_expiry','cpc_expiry','CPC'),
        ]:
            expiry = getattr(vehicle, field)
            if not expiry: continue
            days_left = (expiry - today).days
            if days_left == 14 or 0 <= days_left <= 7:
                sev = 'high' if 0 <= days_left <= 7 else 'medium'
                Notification.objects.get_or_create(
                    notification_type=ntype, related_vehicle=vehicle,
                    created_at__date=today,
                    defaults={
                        'title': f'Vehicle {label} Expiring Soon',
                        'message': f"{vehicle.plate_number} {label} expires in {days_left} days ({expiry}).",
                        'severity': sev, 'related_vehicle': vehicle,
                    }
                )

    for payment in Payment.objects.filter(status='overdue').select_related('contract','contract__driver'):
        days_over = (today - payment.due_date).days
        Notification.objects.get_or_create(
            notification_type='payment_overdue', related_payment=payment,
            created_at__date=today,
            defaults={
                'title': 'Overdue Payment',
                'message': f"Payment of ₱{payment.balance:,.2f} is {days_over} day/s overdue (Due: {payment.due_date}).",
                'severity': 'high', 'related_payment': payment,
                'related_contract': payment.contract,
            }
        )
