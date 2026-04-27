from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Driver, Vehicle

# Create your views here.
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request,'home.html', {})

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
            messages.error(request, 'Username or password is incorrect')
    return render(request,'login.html', {})

def logout_user(request):
    logout(request)
    return redirect('login')

# ── Drivers ──────────────────────────────────────────────────────────────────

@login_required
def drivers(request):
    q = request.GET.get('q','')
    qs = Driver.objects.all()
    if q:
        qs = qs.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(license_number__icontains=q)|Q(phone__icontains=q)|Q(email__icontains=q))
    ctx = {'drivers': qs, 'q': q}
    return render(request, 'drivers.html', ctx)


@login_required
@require_POST
def driver_add(request):
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
    return redirect('drivers')


@login_required
@require_POST
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
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
    return redirect('drivers')


@login_required
@require_POST
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    try:
        driver.delete()
        messages.success(request, 'Driver deleted.')
    except Exception as e:
        messages.error(request, f'Cannot delete: {e}')
    return redirect('drivers')

# ── Vehicles ─────────────────────────────────────────────────────────────────

@login_required
def vehicles(request):
    q = request.GET.get('q','')
    qs = Vehicle.objects.all()
    if q:
        qs = qs.filter(Q(plate_number__icontains=q)|Q(brand__icontains=q)|Q(model__icontains=q))
    ctx = {'vehicles': qs, 'q': q}
    return render(request, 'vehicles.html', ctx)


@login_required
@require_POST
def vehicle_add(request):
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
    return redirect('vehicles')


@login_required
@require_POST
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
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
    return redirect('vehicles')


@login_required
@require_POST
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    try:
        vehicle.delete()
        messages.success(request, 'Vehicle deleted.')
    except Exception as e:
        messages.error(request, f'Cannot delete: {e}')
    return redirect('vehicles')


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


def repairs(request):
    if request.user.is_authenticated:
        return render(request, 'repairs.html', {})

def payments(request):
    if request.user.is_authenticated:
        return render(request, 'payments.html', {})


def contracts(request):
    if request.user.is_authenticated:
        return render(request, 'contracts.html', {})

def notifications(request):
    if request.user.is_authenticated:
        return render(request, 'notifications.html', {})


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
