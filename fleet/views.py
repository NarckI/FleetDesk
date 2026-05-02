from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, Case, When, Value, IntegerField
from decimal import Decimal
from datetime import date
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Driver, Vehicle, Contract, Payment, Repair, Notification, RepairReceipt
from .services import auto_expire_contracts, run_daily_tasks, mark_overdue_payments, generate_daily_payments


# Create your views here.

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect', extra_tags='login')
    return render(request,'login.html', {})

def logout_user(request):
    logout(request)
    return redirect('login')
# ── Dashboard ──────────────────────────────────────────────────────────────────
@login_required
def home(request):
    run_daily_tasks()
    recent_contracts = Contract.objects.select_related('driver','vehicle').order_by('-created_at')[:6]
    recent_payments = Payment.objects.select_related('contract__driver').order_by('-created_at')[:6]
    paid_agg = Payment.objects.filter(status='paid').aggregate(t=Sum('amount_paid'))
    ctx = {
        'total_drivers': Driver.objects.count(),
        'active_drivers': Driver.objects.filter(status='active').count(),
        'total_vehicles': Vehicle.objects.count(),
        'available_vehicles': Vehicle.objects.filter(status='available').count(),
        'active_contracts': Contract.objects.filter(status='active').count(),
        'recent_contracts': recent_contracts,
        'revenue_paid': paid_agg['t'] or 0,
        'payment_count': Payment.objects.filter(status='paid').count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
        'overdue_payments': Payment.objects.filter(status='overdue').count(),
        'recent_payments': recent_payments,
        'unread_notifications': Notification.objects.filter(is_read=False).count(),
    }
    return render(request, 'home.html', ctx)

# ── Drivers ──────────────────────────────────────────────────────────────────

@login_required
def drivers(request):
    q = request.GET.get('q','')
    page_number = request.GET.get('page')
    qs = Driver.objects.all().annotate(
        status_order=Case(
            When(status='suspended', then=Value(2)),
            When(status='inactive', then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-created_at')
    if q:
        qs = qs.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(license_number__icontains=q)|Q(phone__icontains=q)|Q(email__icontains=q))
    paginator = Paginator(qs, 10)
    drivers_page = paginator.get_page(page_number)
    ctx = {'drivers': drivers_page, 'q': q, 'unread_notifications': Notification.objects.filter(is_read=False).count()}
    return render(request, 'drivers.html', ctx)


@login_required
@require_POST
def driver_add(request):
    page = request.POST.get('page', 1)
    try:
        Driver.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            license_number=request.POST['license_number'],
            phone=request.POST.get('phone',''),
            email=request.POST.get('email',''),
            address=request.POST.get('address',''),
            license_expiry=request.POST['license_expiry'],
            date_joined=request.POST.get('date_joined') or date.today(),
            status=request.POST.get('status','active'),
        )
        messages.success(request, 'Driver added successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('drivers')}?page={page}")


@login_required
@require_POST
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    page = request.POST.get('page', 1)
    try:
        driver.first_name = request.POST['first_name']
        driver.last_name = request.POST['last_name']
        driver.license_number = request.POST['license_number']
        driver.phone = request.POST.get('phone','')
        driver.email = request.POST.get('email','')
        driver.address = request.POST.get('address','')
        driver.license_expiry = request.POST['license_expiry']
        driver.date_joined = request.POST.get('date_joined') or driver.date_joined
        driver.status = request.POST.get('status','active')
        driver.save()
        messages.success(request, 'Driver updated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('drivers')}?page={page}")


@login_required
@require_POST
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    page = request.POST.get('page', 1)
    try:
        driver.delete()
        messages.success(request, 'Driver deleted.')
    except Exception as e:
        messages.error(request, f'Cannot delete: {e}')
    return redirect(f"{reverse('drivers')}?page={page}")

# ── Vehicles ─────────────────────────────────────────────────────────────────

@login_required
def vehicles(request):
    q = request.GET.get('q','')
    page_number = request.GET.get('page')
    qs = Vehicle.objects.all()
    if q:
        qs = qs.filter(Q(plate_number__icontains=q)|Q(brand__icontains=q)|Q(model__icontains=q))
    paginator = Paginator(qs, 10)
    vehicles_page = paginator.get_page(page_number)
    ctx = {'vehicles': vehicles_page, 'q': q, 'unread_notifications': Notification.objects.filter(is_read=False).count()}
    return render(request, 'vehicles.html', ctx)


@login_required
@require_POST
def vehicle_add(request):
    page = request.POST.get('page', 1)
    try:
        Vehicle.objects.create(
            plate_number=request.POST['plate_number'],
            vehicle_registration=request.POST.get('vehicle_registration',''),
            vehicle_type=request.POST['vehicle_type'],
            brand=request.POST['brand'],
            model=request.POST['model'],
            year=int(request.POST['year']),
            mileage=int(request.POST.get('mileage') or 0),
            last_maintenance=request.POST.get('last_maintenance') or None,
            status=request.POST.get('status','available'),
            or_expiry=request.POST.get('or_expiry') or None,
            cr_expiry=request.POST.get('cr_expiry') or None,
            cpc_expiry=request.POST.get('cpc_expiry') or None,
        )
        messages.success(request, 'Vehicle added successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('vehicles')}?page={page}")


@login_required
@require_POST
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    page = request.POST.get('page', 1)
    try:
        vehicle.plate_number = request.POST['plate_number']
        vehicle.vehicle_registration = request.POST.get('vehicle_registration','')
        vehicle.vehicle_type = request.POST['vehicle_type']
        vehicle.brand = request.POST['brand']
        vehicle.model = request.POST['model']
        vehicle.year = int(request.POST['year'])
        vehicle.mileage = int(request.POST.get('mileage') or 0)
        vehicle.last_maintenance = request.POST.get('last_maintenance') or None
        vehicle.status = request.POST.get('status', vehicle.status)
        vehicle.or_expiry = request.POST.get('or_expiry') or None
        vehicle.cr_expiry = request.POST.get('cr_expiry') or None
        vehicle.cpc_expiry = request.POST.get('cpc_expiry') or None
        vehicle.save()
        messages.success(request, 'Vehicle updated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('vehicles')}?page={page}")


@login_required
@require_POST
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    page = request.POST.get('page', 1)
    try:
        vehicle.delete()
        messages.success(request, 'Vehicle deleted.')
    except Exception as e:
        messages.error(request, f'Cannot delete: {e}')
    return redirect(f"{reverse('vehicles')}?page={page}")


@login_required
@require_POST
def vehicle_create_repair(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    active_contract = vehicle.contracts.filter(status='active').select_related('driver').first()
    repair = Repair.objects.create(
        vehicle=vehicle,
        driver=active_contract.driver if active_contract else None,
        status='pending',
    )
    vehicle.status = 'maintenance'
    vehicle.save(update_fields=['status'])
    messages.success(request, f'Repair log created for {vehicle.plate_number}.')
    return redirect('repairs')

# ── Contracts ─────────────────────────────────────────────────────────────────

@login_required
def contracts(request):
    auto_expire_contracts()
    q = request.GET.get('q','')
    page_number = request.GET.get('page')
    qs = Contract.objects.select_related('driver','vehicle').annotate(
        status_order=Case(
            When(status='terminated', then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-created_at')
    if q:
        qs = qs.filter(Q(driver__first_name__icontains=q)|Q(driver__last_name__icontains=q)|Q(vehicle__plate_number__icontains=q))

    # For dropdowns — filtered
    available_drivers = Driver.objects.filter(status='active').exclude(
        contracts__status='active'
    )
    available_vehicles = Vehicle.objects.filter(status='available')

    paginator = Paginator(qs, 10)
    contracts_page = paginator.get_page(page_number)

    ctx = {
        'contracts': contracts_page, 'q': q,
        'available_drivers': available_drivers,
        'available_vehicles': available_vehicles,
        'unread_notifications': Notification.objects.filter(is_read=False).count(),
    }
    return render(request, 'contracts.html', ctx)


@login_required
@require_POST
def contract_add(request):
    page = request.POST.get('page', 1)
    try:
        start_date = date.fromisoformat(request.POST['start_date'])
        contract = Contract.objects.create(
            driver_id=request.POST['driver'],
            vehicle_id=request.POST['vehicle'],
            daily_rate=Decimal(request.POST['daily_rate']),
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            status=request.POST.get('status','active'),
        )
        # Create today's payment if contract is active today
        today = date.today()
        if contract.status == 'active' and start_date == today:
            Payment.objects.get_or_create(
                contract=contract, due_date=today,
                defaults={'amount': contract.daily_rate, 'balance': contract.daily_rate, 'status': 'pending'}
            )
            messages.success(request, 'Payment generated successfully.')
        messages.success(request, 'Contract added successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('contracts')}?page={page}")


@login_required
@require_POST
def contract_edit(request, pk):
    page = request.POST.get('page', 1)
    contract = get_object_or_404(Contract, pk=pk)
    if contract.status == 'terminated':
        messages.error(request, 'Terminated contracts cannot be edited.')
        return redirect('contracts')
    try:
        contract.start_date = date.fromisoformat(request.POST['start_date'])
        contract.end_date = date.fromisoformat(request.POST['end_date'])
        contract.driver_id = request.POST['driver']
        contract.vehicle_id = request.POST['vehicle']
        contract.daily_rate = Decimal(request.POST['daily_rate'])
        contract.status = request.POST.get('status', contract.status)
        contract.save()
        messages.success(request, 'Contract updated.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('contracts')}?page={page}")


@login_required
@require_POST
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    page = request.POST.get('page', 1)
    try:
        contract.status = 'terminated'
        contract.save(update_fields=['status'])
        messages.success(request, 'Contract terminated. Payment history preserved.')
    except Exception as e:
        messages.error(request, f'Cannot delete: {e}')
    return redirect(f"{reverse('contracts')}?page={page}")





# ── Payments ──────────────────────────────────────────────────────────────────

@login_required
def payments(request):
    mark_overdue_payments()
    generate_daily_payments()
    status_filter = request.GET.get('status','')
    q = request.GET.get('q','')
    page_number = request.GET.get('page')
    qs = Payment.objects.select_related('contract__driver','contract__vehicle').annotate(
        status_order=Case(
            When(status='paid', then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('-due_date', 'status_order', 'balance')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if q:
        qs = qs.filter(Q(contract__driver__first_name__icontains=q)|Q(contract__driver__last_name__icontains=q))

    total_paid = Payment.objects.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0
    total_pending = Payment.objects.filter(status='pending').aggregate(t=Sum('balance'))['t'] or 0
    total_overdue = Payment.objects.filter(status='overdue').aggregate(t=Sum('balance'))['t'] or 0
    payment_count = Payment.objects.filter(status='paid').count()
    pending_count = Payment.objects.filter(status='pending').count()
    overdue_count = Payment.objects.filter(status='overdue').count()

    paginator = Paginator(qs, 20)
    payments_page = paginator.get_page(page_number)

    ctx = {
        'payments': payments_page, 'status_filter': status_filter, 'q': q,
        'total_paid': total_paid, 'total_pending': total_pending, 'total_overdue': total_overdue,
        'pending_count': pending_count, 'overdue_count': overdue_count, 'payment_count': payment_count,
        'unread_notifications': Notification.objects.filter(is_read=False).count(),
    }
    return render(request, 'payments.html', ctx)


@login_required
@require_POST
def payment_mark_paid(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    page = request.POST.get('page', 1)
    payment.amount_paid = payment.amount
    payment.balance = Decimal('0')
    payment.paid_date = date.today()
    payment.status = 'paid'
    payment.save()
    messages.success(request, 'Payment marked as paid.')
    return redirect(f"{reverse('payments')}?page={page}")


@login_required
@require_POST
def payment_partial(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    page = request.POST.get('page', 1)
    try:
        amount = Decimal(request.POST['amount'])
        if amount <= 0:
            raise ValueError('Amount must be positive')
        if amount > payment.balance:
            raise ValueError('Amount exceeds balance')
        payment.amount_paid += amount
        payment.balance = payment.amount - payment.amount_paid
        payment.paid_date = date.today()
        payment.status = 'paid' if payment.balance <= 0 else 'partial'
        payment.save()
        messages.success(request, f'Partial payment of ₱{amount:,.2f} recorded.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('payments')}?page={page}")


@login_required
@require_POST
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    page = request.POST.get('page', 1)
    try:
        payment.delete()
        messages.success(request, 'Payment deleted.')
    except Exception as e:
        messages.error(request, f'Cannot delete payment: {e}')
    return redirect(f"{reverse('payments')}?page={page}")

# ── Repairs ───────────────────────────────────────────────────────────────────

REPAIR_CHECKLIST = [
    ("ENGINE AND POWERTRAIN", [
        "Engine diagnostics and troubleshooting","Spark plug replacement","Ignition coil replacement",
        "Fuel injector cleaning or replacement","Fuel pump repair","Air filter replacement",
        "Timing belt or timing chain replacement","Serpentine belt replacement",
        "Radiator repair or replacement","Water pump replacement","Thermostat replacement",
        "Engine mount replacement","Head gasket repair","Engine overhaul or rebuild",
        "Transmission fluid change","Transmission repair or rebuild","Clutch replacement for manual",
        "Differential repair","Driveshaft and CV joint repair",
    ]),
    ("OIL AND FLUID SERVICES", [
        "Engine oil and oil filter change","Transmission fluid change","Brake fluid flush",
        "Power steering fluid replacement","Coolant flush and refill","Differential fluid change",
        "Windshield washer fluid refill",
    ]),
    ("BRAKE SYSTEM", [
        "Brake pad replacement","Brake shoe replacement","Brake disc or rotor resurfacing or replacement",
        "Brake caliper repair or replacement","Brake master cylinder repair","Brake fluid bleeding",
        "ABS diagnostics and repair","Brake line repair",
    ]),
    ("SUSPENSION AND STEERING", [
        "Shock absorber replacement","Strut replacement","Coil spring replacement",
        "Control arm repair","Ball joint replacement","Tie rod end replacement",
        "Steering rack repair or replacement","Power steering pump repair",
        "Wheel alignment","Wheel balancing",
    ]),
    ("AIR CONDITIONING AND HVAC", [
        "AC system diagnostics","Refrigerant recharge","Compressor repair or replacement",
        "Condenser repair or replacement","Evaporator repair","Blower motor replacement",
        "Cabin air filter replacement","AC leak detection and sealing",
    ]),
    ("ELECTRICAL SYSTEM", [
        "Battery replacement","Alternator repair or replacement","Starter motor repair",
        "Fuse and relay replacement","Wiring repair","Lighting system repair",
        "Power window motor repair","Central locking system repair","ECU diagnostics and repair",
        "Sensor replacement",
    ]),
    ("BODY AND EXTERIOR", [
        "Dent repair","Paint touch up or repaint","Bumper repair or replacement",
        "Windshield repair or replacement","Side mirror replacement",
        "Headlight restoration or replacement","Rust removal and treatment",
        "Door alignment and hinge repair",
    ]),
    ("INTERIOR", [
        "Seat repair or reupholstery","Dashboard repair","Carpet cleaning or replacement",
        "Headliner repair","Power seat motor repair","Interior trim repair",
        "Infotainment system repair or upgrade","Airbag system repair",
    ]),
    ("TIRES AND WHEELS", [
        "Tire replacement","Tire rotation","Wheel alignment","Wheel balancing",
        "Puncture repair","Rim repair or replacement",
    ]),
    ("EXHAUST SYSTEM", [
        "Muffler repair or replacement","Exhaust pipe repair",
        "Catalytic converter replacement","Oxygen sensor replacement",
    ]),
    ("COOLING SYSTEM", [
        "Radiator flush","Hose replacement","Cooling fan repair","Coolant leak repair",
    ]),
    ("SAFETY AND DRIVER ASSIST", [
        "Airbag diagnostics and repair","Parking sensor repair",
        "Backup camera repair","ADAS calibration for newer vehicles",
    ]),
]


@login_required
def repairs(request):
    q = request.GET.get('q','')
    page_number = request.GET.get('page')
    qs = Repair.objects.select_related('vehicle','driver').prefetch_related('receipts').all()
    if q:
        qs = qs.filter(Q(vehicle__plate_number__icontains=q)|Q(vehicle__brand__icontains=q)|Q(vehicle__model__icontains=q))

    paginator = Paginator(qs, 10)
    repairs_page = paginator.get_page(page_number)
    ctx = {
        'repairs': repairs_page, 'q': q,
        'checklist_groups': REPAIR_CHECKLIST,
        'unread_notifications': Notification.objects.filter(is_read=False).count(),
    }
    return render(request, 'repairs.html', ctx)


@login_required
@require_POST
def repair_save_details(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    page = request.POST.get('page', 1)
    try:
        repair.date_finished = request.POST.get('date_finished') or None
        repair.repair_shop_name = request.POST.get('repair_shop_name','')
        repair.total_cost = Decimal(request.POST.get('total_cost') or 0)
        repair.repair_details = request.POST.get('repair_details','')
        repair.checklist = request.POST.getlist('checklist')
        repair.status = 'completed' if repair.date_finished else 'in-progress'
        repair.save()

        # Handle file uploads
        for f in request.FILES.getlist('receipts'):
            RepairReceipt.objects.create(repair=repair, file=f, file_name=f.name)

        # If completed, restore vehicle
        if repair.status == 'completed':
            vehicle = repair.vehicle
            has_active = vehicle.contracts.filter(status='active').exists()
            vehicle.status = 'in-use' if has_active else 'available'
            if repair.date_finished:
                vehicle.last_maintenance = repair.date_finished
            vehicle.save()

        messages.success(request, 'Repair details saved.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect(f"{reverse('repairs')}?page={page}")


@login_required
@require_POST
def repair_mark_completed(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    page = request.POST.get('page', 1)
    repair.status = 'completed'
    if not repair.date_finished:
        repair.date_finished = date.today()
    repair.save()
    # Restore vehicle status
    vehicle = repair.vehicle
    has_active = vehicle.contracts.filter(status='active').exists()
    vehicle.status = 'in-use' if has_active else 'available'
    vehicle.last_maintenance = repair.date_finished
    vehicle.save()
    messages.success(request, f'Repair for {vehicle.plate_number} marked as completed.')
    return redirect(f"{reverse('repairs')}?page={page}")


@login_required
@require_POST
def repair_delete(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    vehicle = repair.vehicle
    page = request.POST.get('page', 1)
    has_active = vehicle.contracts.filter(status='active').exists()
    vehicle.status = 'in-use' if has_active else 'available'
    vehicle.save()
    repair.delete()
    messages.success(request, 'Repair log deleted.')
    return redirect(f"{reverse('repairs')}?page={page}")


def repair_detail_json(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    receipts = [{'id': r.id, 'file_name': r.file_name, 'url': r.file.url} for r in repair.receipts.all()]
    data = {
        'id': repair.id,
        'plate_number': repair.vehicle.plate_number,
        'vehicle': f"{repair.vehicle.brand} {repair.vehicle.model} ({repair.vehicle.year})",
        'vehicle_type': repair.vehicle.get_vehicle_type_display(),
        'driver': repair.driver.full_name if repair.driver else '—',
        'date_finished': str(repair.date_finished) if repair.date_finished else '',
        'repair_shop_name': repair.repair_shop_name,
        'total_cost': str(repair.total_cost),
        'repair_details': repair.repair_details,
        'checklist': repair.checklist,
        'status': repair.status,
        'receipts': receipts,
    }
    return JsonResponse(data)


# ── Notifications ─────────────────────────────────────────────────────────────

@login_required
def notifications(request):
    from .services import generate_notifications
    generate_notifications()
    notif_type = request.GET.get('type','')
    qs = Notification.objects.all()
    if notif_type == 'payment':
        qs = qs.filter(notification_type='payment_overdue')
    elif notif_type == 'expiry':
        qs = qs.filter(notification_type__in=['license_expiry','or_expiry','cr_expiry','cpc_expiry'])
    payment_count = Notification.objects.filter(notification_type='payment_overdue').count()
    expiry_count = Notification.objects.filter(notification_type__in=['license_expiry','or_expiry','cr_expiry','cpc_expiry']).count()
    ctx = {
        'notifications': qs,
        'notif_type': notif_type,
        'payment_count': payment_count,
        'expiry_count': expiry_count,
        'total_count': payment_count + expiry_count,
        'unread_notifications': Notification.objects.filter(is_read=False).count(),
    }
    return render(request, 'notifications.html', ctx)


@login_required
@require_POST
def notification_mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk)
    type_filter = request.POST.get('type', '')
    n.is_read = True
    n.save()
    if type_filter:
        return redirect(f"/notifications/?type={type_filter}")
    return redirect("notifications")


@login_required
@require_POST
def notification_mark_all_read(request):
    type_filter = request.POST.get('type', '')
    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    if type_filter:
        return redirect(f"/notifications/?type={type_filter}")
    return redirect("notifications")



# ----- AJAX Helpers -----

@login_required
def driver_data_json(request, pk):
    d = get_object_or_404(Driver, pk=pk)
    return JsonResponse({
        'id': d.id, 'first_name': d.first_name, 'last_name': d.last_name,
        'license_number': d.license_number, 'phone': d.phone, 'email': d.email,
        'address': d.address,
        'license_expiry': str(d.license_expiry),
        'date_joined': str(d.date_joined),
        'status': d.status,
    })

@login_required
def vehicle_data_json(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    return JsonResponse({
        'id': v.id, 'plate_number': v.plate_number, 'vehicle_registration': v.vehicle_registration,
        'vehicle_type': v.vehicle_type, 'brand': v.brand, 'model': v.model,
        'year': v.year, 'mileage': v.mileage,
        'last_maintenance': str(v.last_maintenance) if v.last_maintenance else '',
        'status': v.status,
        'or_expiry': str(v.or_expiry) if v.or_expiry else '',
        'cr_expiry': str(v.cr_expiry) if v.cr_expiry else '',
        'cpc_expiry': str(v.cpc_expiry) if v.cpc_expiry else '',
    })

@login_required
def contract_drivers_json(request):
    """Available drivers for contract modal (active, no active contract)"""
    exclude_ids = Contract.objects.filter(status='active').values_list('driver_id', flat=True)
    qs = Driver.objects.filter(status='active').exclude(id__in=exclude_ids)
    return JsonResponse({'drivers': list(qs.values('id','first_name','last_name'))})


@login_required
def contract_vehicles_json(request):
    """Available vehicles for contract modal"""
    qs = Vehicle.objects.filter(status='available')
    return JsonResponse({'vehicles': list(qs.values('id','plate_number','brand','model'))})


@login_required
def contract_data_json(request, pk):
    """Contract data for edit modal"""
    c = get_object_or_404(Contract, pk=pk)
    return JsonResponse({
        'id': c.id,
        'driver_id': c.driver_id,
        'vehicle_id': c.vehicle_id,
        'daily_rate': str(c.daily_rate),
        'start_date': str(c.start_date),
        'end_date': str(c.end_date),
        'status': c.status,
        'driver_name': c.driver.full_name,
        'vehicle_display': str(c.vehicle),
    })
