from datetime import date

from django.db import connection, transaction
from django.utils import timezone

from .models import Contract, Driver, Notification, Payment, Repair, Vehicle


def _fetchall_dicts(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _status_display(value):
    return '' if value is None else str(value).replace('-', ' ').title()


def _vehicle_type_display(value):
    if value == '4-seater':
        return '4 Seater'
    if value == '7-seater':
        return '7 Seater'
    return _status_display(value)


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


def fetch_recent_contracts(limit=6):
    contract_table = Contract._meta.db_table
    driver_table = Driver._meta.db_table
    vehicle_table = Vehicle._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                c.id AS pk,
                c.start_date,
                c.end_date,
                c.daily_rate,
                c.status,
                c.created_at,
                d.first_name,
                d.last_name,
                v.plate_number,
                v.brand,
                v.model
              FROM {contract_table} c
              JOIN {driver_table} d ON c.driver_id = d.id
              JOIN {vehicle_table} v ON c.vehicle_id = v.id
             ORDER BY c.created_at DESC
             LIMIT %s
            """,
            [limit],
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'daily_rate': row['daily_rate'],
            'status': row['status'],
            'status_display': _status_display(row['status']),
            'created_at': row['created_at'],
            'driver': {'full_name': f"{row['first_name']} {row['last_name']}"},
            'vehicle': {
                'plate_number': row['plate_number'],
                'brand': row['brand'],
                'model': row['model'],
            },
        }
        for row in rows
    ]


def fetch_recent_payments(limit=6):
    payment_table = Payment._meta.db_table
    contract_table = Contract._meta.db_table
    driver_table = Driver._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                p.id AS pk,
                p.amount,
                p.due_date,
                p.paid_date,
                p.balance,
                p.status,
                p.created_at,
                c.id AS contract_pk,
                d.first_name,
                d.last_name
              FROM {payment_table} p
              JOIN {contract_table} c ON p.contract_id = c.id
              JOIN {driver_table} d ON c.driver_id = d.id
             ORDER BY p.created_at DESC
             LIMIT %s
            """,
            [limit],
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'amount': row['amount'],
            'due_date': row['due_date'],
            'paid_date': row['paid_date'],
            'balance': row['balance'],
            'status': row['status'],
            'status_display': _status_display(row['status']),
            'created_at': row['created_at'],
            'contract': {
                'pk': row['contract_pk'],
                'driver': {'full_name': f"{row['first_name']} {row['last_name']}"},
            },
        }
        for row in rows
    ]


def fetch_driver_rows(query=None):
    driver_table = Driver._meta.db_table
    params = []
    where = ""
    if query:
        where = """
        WHERE (
            first_name ILIKE %s OR
            last_name ILIKE %s OR
            license_number ILIKE %s OR
            phone ILIKE %s OR
            email ILIKE %s
        )
        """
        like = f"%{query}%"
        params.extend([like, like, like, like, like])

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                id AS pk,
                first_name,
                last_name,
                license_number,
                phone,
                email,
                address,
                license_expiry,
                date_joined,
                status,
                created_at
              FROM {driver_table}
              {where}
             ORDER BY
                CASE
                    WHEN status = 'suspended' THEN 2
                    WHEN status = 'inactive' THEN 1
                    ELSE 0
                END,
                created_at DESC
            """,
            params,
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'full_name': f"{row['first_name']} {row['last_name']}",
            'license_number': row['license_number'],
            'phone': row['phone'],
            'email': row['email'],
            'address': row['address'],
            'license_expiry': row['license_expiry'],
            'date_joined': row['date_joined'],
            'status': row['status'],
            'created_at': row['created_at'],
        }
        for row in rows
    ]


def fetch_vehicle_rows(query=None):
    vehicle_table = Vehicle._meta.db_table
    params = []
    where = ""
    if query:
        where = """
        WHERE (
            plate_number ILIKE %s OR
            brand ILIKE %s OR
            model ILIKE %s
        )
        """
        like = f"%{query}%"
        params.extend([like, like, like])

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                id AS pk,
                plate_number,
                vehicle_registration,
                vehicle_type,
                brand,
                model,
                year,
                mileage,
                last_maintenance,
                status,
                or_expiry,
                cr_expiry,
                cpc_expiry,
                created_at,
                CASE vehicle_type
                    WHEN '4-seater' THEN '4 Seater'
                    WHEN '7-seater' THEN '7 Seater'
                    ELSE vehicle_type
                END AS get_vehicle_type_display
              FROM {vehicle_table}
              {where}
             ORDER BY plate_number
            """,
            params,
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'plate_number': row['plate_number'],
            'vehicle_registration': row['vehicle_registration'],
            'vehicle_type': row['vehicle_type'],
            'vehicle_type_display': row['get_vehicle_type_display'],
            'get_vehicle_type_display': row['get_vehicle_type_display'],
            'brand': row['brand'],
            'model': row['model'],
            'year': row['year'],
            'mileage': row['mileage'],
            'last_maintenance': row['last_maintenance'],
            'status': row['status'],
            'status_display': _status_display(row['status']),
            'or_expiry': row['or_expiry'],
            'cr_expiry': row['cr_expiry'],
            'cpc_expiry': row['cpc_expiry'],
            'created_at': row['created_at'],
        }
        for row in rows
    ]


def fetch_contract_rows(query=None):
    contract_table = Contract._meta.db_table
    driver_table = Driver._meta.db_table
    vehicle_table = Vehicle._meta.db_table
    params = []
    where = ""
    if query:
        where = """
        WHERE (
            d.first_name ILIKE %s OR
            d.last_name ILIKE %s OR
            v.plate_number ILIKE %s
        )
        """
        like = f"%{query}%"
        params.extend([like, like, like])

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                c.id AS pk,
                c.start_date,
                c.end_date,
                c.daily_rate,
                c.status,
                c.created_at,
                d.first_name,
                d.last_name,
                v.plate_number,
                v.brand,
                v.model
              FROM {contract_table} c
              JOIN {driver_table} d ON c.driver_id = d.id
              JOIN {vehicle_table} v ON c.vehicle_id = v.id
              {where}
             ORDER BY
                CASE WHEN c.status = 'terminated' THEN 1 ELSE 0 END,
                c.created_at DESC
            """,
                params,
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'daily_rate': row['daily_rate'],
            'status': row['status'],
            'status_display': _status_display(row['status']),
            'created_at': row['created_at'],
            'driver': {'full_name': f"{row['first_name']} {row['last_name']}"},
            'vehicle': {
                'plate_number': row['plate_number'],
                'brand': row['brand'],
                'model': row['model'],
            },
        }
        for row in rows
    ]


def fetch_payment_rows(status_filter=None, query=None):
    payment_table = Payment._meta.db_table
    contract_table = Contract._meta.db_table
    driver_table = Driver._meta.db_table
    vehicle_table = Vehicle._meta.db_table

    where = []
    params = []
    if status_filter:
        where.append("p.status = %s")
        params.append(status_filter)
    if query:
        where.append("(d.first_name ILIKE %s OR d.last_name ILIKE %s)")
        like = f"%{query}%"
        params.extend([like, like])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                p.id AS pk,
                p.amount,
                p.due_date,
                p.paid_date,
                p.balance,
                p.status,
                p.created_at,
                c.id AS contract_pk,
                d.first_name,
                d.last_name,
                v.id AS vehicle_pk,
                v.plate_number,
                v.brand,
                v.model
              FROM {payment_table} p
              JOIN {contract_table} c ON p.contract_id = c.id
              JOIN {driver_table} d ON c.driver_id = d.id
              JOIN {vehicle_table} v ON c.vehicle_id = v.id
              {where_sql}
             ORDER BY
                p.due_date DESC,
                CASE WHEN p.status = 'paid' THEN 1 ELSE 0 END,
                p.balance
            """,
            params,
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'amount': row['amount'],
            'due_date': row['due_date'],
            'paid_date': row['paid_date'],
            'balance': row['balance'],
            'status': row['status'],
            'status_display': _status_display(row['status']),
            'created_at': row['created_at'],
            'contract': {
                'pk': row['contract_pk'],
                'driver': {'full_name': f"{row['first_name']} {row['last_name']}"},
                'vehicle': {
                    'pk': row['vehicle_pk'],
                    'plate_number': row['plate_number'],
                    'brand': row['brand'],
                    'model': row['model'],
                },
            },
        }
        for row in rows
    ]


def fetch_repair_rows(query=None):
    repair_table = Repair._meta.db_table
    vehicle_table = Vehicle._meta.db_table
    driver_table = Driver._meta.db_table
    params = []
    where = ""
    if query:
        where = """
        WHERE (
            v.plate_number ILIKE %s OR
            v.brand ILIKE %s OR
            v.model ILIKE %s
        )
        """
        like = f"%{query}%"
        params.extend([like, like, like])

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                r.id AS pk,
                r.date_finished,
                r.status,
                r.created_at,
                r.total_cost,
                r.repair_details,
                r.repair_shop_name,
                r.checklist,
                v.plate_number,
                v.brand,
                v.model,
                v.year,
                v.vehicle_type,
                d.first_name,
                d.last_name
              FROM {repair_table} r
              JOIN {vehicle_table} v ON r.vehicle_id = v.id
              LEFT JOIN {driver_table} d ON r.driver_id = d.id
              {where}
             ORDER BY r.created_at DESC
            """,
            params,
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'pk': row['pk'],
            'date_finished': row['date_finished'],
            'status': row['status'],
            'created_at': row['created_at'],
            'total_cost': row['total_cost'],
            'repair_details': row['repair_details'],
            'repair_shop_name': row['repair_shop_name'],
            'checklist': row['checklist'],
            'status_display': _status_display(row['status']),
            'vehicle': {
                'plate_number': row['plate_number'],
                'brand': row['brand'],
                'model': row['model'],
                'year': row['year'],
                'vehicle_type_display': _vehicle_type_display(row['vehicle_type']),
                'get_vehicle_type_display': _vehicle_type_display(row['vehicle_type']),
            },
            'driver': {
                'full_name': f"{row['first_name']} {row['last_name']}".strip() if row['first_name'] else None,
            },
        }
        for row in rows
    ]


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
    today = _today(today)
    driver_table = Driver._meta.db_table
    vehicle_table = Vehicle._meta.db_table
    payment_table = Payment._meta.db_table
    notification_table = Notification._meta.db_table

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO {notification_table}
                (notification_type, title, message, severity, is_read, related_driver_id, related_vehicle_id, related_contract_id, related_payment_id, created_at)
            SELECT
                'license_expiry',
                'Driver License Expiring Soon',
                d.first_name || ' ' || d.last_name || '''s license expires in ' || (d.license_expiry - %s) || ' days (' || d.license_expiry || ').',
                CASE
                    WHEN (d.license_expiry - %s) BETWEEN 0 AND 7 THEN 'high'
                    ELSE 'medium'
                END,
                FALSE,
                d.id,
                NULL,
                NULL,
                NULL,
                NOW()
              FROM {driver_table} d
             WHERE d.status = 'active'
               AND d.license_expiry IS NOT NULL
               AND (
                    d.license_expiry - %s = 21
                    OR (d.license_expiry - %s) BETWEEN 0 AND 14
               )
               AND NOT EXISTS (
                   SELECT 1
                     FROM {notification_table} n
                    WHERE n.notification_type = 'license_expiry'
                      AND n.related_driver_id = d.id
                      AND n.created_at::date = %s
               )
            """,
            [today, today, today, today, today],
        )

        for field, label in [('or_expiry', 'OR'), ('cr_expiry', 'CR'), ('cpc_expiry', 'CPC')]:
            cursor.execute(
                f"""
                INSERT INTO {notification_table}
                    (notification_type, title, message, severity, is_read, related_driver_id, related_vehicle_id, related_contract_id, related_payment_id, created_at)
                SELECT
                    %s,
                    %s,
                    v.plate_number || ' ' || %s || ' expires in ' || (v.{field} - %s) || ' days (' || v.{field} || ').',
                    CASE
                        WHEN (v.{field} - %s) BETWEEN 0 AND 7 THEN 'high'
                        ELSE 'medium'
                    END,
                    FALSE,
                    NULL,
                    v.id,
                    NULL,
                    NULL,
                    NOW()
                  FROM {vehicle_table} v
                 WHERE v.{field} IS NOT NULL
                   AND (
                        v.{field} - %s = 14
                        OR (v.{field} - %s) BETWEEN 0 AND 7
                   )
                   AND NOT EXISTS (
                       SELECT 1
                         FROM {notification_table} n
                        WHERE n.notification_type = %s
                          AND n.related_vehicle_id = v.id
                          AND n.created_at::date = %s
                   )
                """,
                [label.lower() + '_expiry', f'Vehicle {label} Expiring Soon', label, today, today, today, today, label.lower() + '_expiry', today],
            )

        cursor.execute(
            f"""
            INSERT INTO {notification_table}
                (notification_type, title, message, severity, is_read, related_driver_id, related_vehicle_id, related_contract_id, related_payment_id, created_at)
            SELECT
                'payment_overdue',
                'Overdue Payment',
                'Payment of ₱' || TO_CHAR(p.balance, 'FM999,999,999,990.00') || ' is ' || (%s - p.due_date) || ' day/s overdue (Due: ' || p.due_date || ').',
                'high',
                FALSE,
                NULL,
                NULL,
                c.id,
                p.id,
                NOW()
              FROM {payment_table} p
              JOIN {Contract._meta.db_table} c ON p.contract_id = c.id
             WHERE p.status = 'overdue'
               AND NOT EXISTS (
                   SELECT 1
                     FROM {notification_table} n
                    WHERE n.notification_type = 'payment_overdue'
                      AND n.related_payment_id = p.id
                      AND n.created_at::date = %s
               )
            """,
            [today, today],
        )

def fetch_available_drivers():
    """Raw SQL: Get drivers with status='active' and no active contracts"""
    driver_table = Driver._meta.db_table
    contract_table = Contract._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                d.id, d.first_name, d.last_name
              FROM {driver_table} d
             WHERE d.status = 'active'
               AND NOT EXISTS (
                   SELECT 1 FROM {contract_table} c
                    WHERE c.driver_id = d.id AND c.status = 'active'
               )
             ORDER BY d.first_name, d.last_name
            """
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'id': row['id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
        }
        for row in rows
    ]


def fetch_available_vehicles():
    """Raw SQL: Get vehicles with status='available'"""
    vehicle_table = Vehicle._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id, plate_number, brand, model
              FROM {vehicle_table}
             WHERE status = 'available'
             ORDER BY plate_number
            """
        )
        rows = _fetchall_dicts(cursor)

    return [
        {
            'id': row['id'],
            'plate_number': row['plate_number'],
            'brand': row['brand'],
            'model': row['model'],
        }
        for row in rows
    ]


def payment_exists_for_contract_date(contract_id, due_date):
    """Raw SQL: Check if payment exists for contract on a given date"""
    payment_table = Payment._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {payment_table} WHERE contract_id = %s AND due_date = %s",
            [contract_id, due_date],
        )
        return cursor.fetchone()[0] > 0


def fetch_notifications(notification_type=None):
    """Raw SQL: Fetch all notifications with optional type filter"""
    notification_table = Notification._meta.db_table

    where = ""
    params = []
    if notification_type:
        where = "WHERE notification_type = %s"
        params = [notification_type]

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT * FROM {notification_table}
            {where}
            ORDER BY created_at DESC
            """,
            params,
        )
        rows = _fetchall_dicts(cursor)

    return rows


def count_notifications_by_type(notification_type):
    """Raw SQL: Count notifications by type"""
    notification_table = Notification._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {notification_table} WHERE notification_type = %s",
            [notification_type],
        )
        return cursor.fetchone()[0]


def mark_notifications_read(notification_type=None):
    """Raw SQL: Mark notifications as read, optionally filtered by type"""
    notification_table = Notification._meta.db_table

    where = ""
    params = []
    if notification_type:
        where = "AND notification_type IN %s"
        params = [tuple(notification_type)]

    with connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE {notification_table} SET is_read = TRUE WHERE is_read = FALSE {where}",
            params,
        )


def vehicle_has_active_contracts(vehicle_id):
    """Raw SQL: Check if vehicle has any active contracts"""
    contract_table = Contract._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {contract_table} WHERE vehicle_id = %s AND status = 'active'",
            [vehicle_id],
        )
        return cursor.fetchone()[0] > 0
