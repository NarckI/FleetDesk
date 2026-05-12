from datetime import date

from django.db import connection, transaction
from django.utils import timezone

from .models import Contract, Driver, Notification, Payment, Vehicle


def count_unread_notifications():
    notification_table = Notification._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {notification_table} WHERE is_read = FALSE"
        )
        return cursor.fetchone()[0]


def get_dashboard_stats():
    driver_table = Driver._meta.db_table
    vehicle_table = Vehicle._meta.db_table
    contract_table = Contract._meta.db_table
    payment_table = Payment._meta.db_table
    notification_table = Notification._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {driver_table}")
        total_drivers = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {driver_table} WHERE status = 'active'")
        active_drivers = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {vehicle_table}")
        total_vehicles = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {vehicle_table} WHERE status = 'available'")
        available_vehicles = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {contract_table} WHERE status = 'active'")
        active_contracts = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT COALESCE(SUM(amount_paid), 0) FROM {payment_table} WHERE status = 'paid'"
        )
        revenue_paid = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {payment_table} WHERE status = 'paid'")
        payment_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {payment_table} WHERE status = 'pending'")
        pending_payments = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {payment_table} WHERE status = 'overdue'")
        overdue_payments = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT COUNT(*) FROM {notification_table} WHERE is_read = FALSE"
        )
        unread_notifications = cursor.fetchone()[0]

    return {
        'total_drivers': total_drivers,
        'active_drivers': active_drivers,
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'active_contracts': active_contracts,
        'revenue_paid': revenue_paid,
        'payment_count': payment_count,
        'pending_payments': pending_payments,
        'overdue_payments': overdue_payments,
        'unread_notifications': unread_notifications,
    }


def _today(today=None):
    return today or timezone.localdate()


def auto_expire_contracts(today=None):
    today = _today(today)
    contract_table = Contract._meta.db_table
    vehicle_table = Vehicle._meta.db_table

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE {contract_table}
               SET status = 'expired', updated_at = NOW()
             WHERE status = 'active'
               AND end_date < %s
            """,
            [today],
        )

        # Keep vehicle status aligned with any remaining active contracts.
        cursor.execute(
            f"""
            UPDATE {vehicle_table} v
               SET status = 'in-use', updated_at = NOW()
             WHERE EXISTS (
                 SELECT 1
                   FROM {contract_table} c
                  WHERE c.vehicle_id = v.id
                    AND c.status = 'active'
             )
            """
        )

        cursor.execute(
            f"""
            UPDATE {vehicle_table} v
               SET status = 'available', updated_at = NOW()
             WHERE v.status <> 'maintenance'
               AND NOT EXISTS (
                   SELECT 1
                     FROM {contract_table} c
                    WHERE c.vehicle_id = v.id
                      AND c.status = 'active'
               )
            """
        )


def run_daily_tasks():
    today = timezone.localdate()
    auto_expire_contracts(today)
    mark_overdue_payments(today)
    generate_daily_payments(today)
    generate_notifications(today)


def mark_overdue_payments(today=None):
    today = _today(today)
    payment_table = Payment._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE {payment_table}
               SET status = 'overdue', updated_at = NOW()
             WHERE due_date < %s
               AND status IN ('pending', 'partial')
            """,
            [today],
        )


def generate_daily_payments(today=None):
    today = _today(today)
    contract_table = Contract._meta.db_table
    payment_table = Payment._meta.db_table

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO {payment_table}
                (contract_id, amount, due_date, paid_date, amount_paid, balance, status, created_at, updated_at)
            SELECT
                c.id,
                c.daily_rate,
                %s,
                NULL,
                0,
                c.daily_rate,
                'pending',
                NOW(),
                NOW()
              FROM {contract_table} c
             WHERE c.status = 'active'
               AND c.start_date <= %s
               AND c.end_date >= %s
               AND NOT EXISTS (
                   SELECT 1
                     FROM {payment_table} p
                    WHERE p.contract_id = c.id
                      AND p.due_date = %s
               )
            """,
            [today, today, today, today],
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
