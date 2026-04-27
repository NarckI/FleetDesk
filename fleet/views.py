from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Driver

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

def repairs(request):
    if request.user.is_authenticated:
        return render(request, 'repairs.html', {})

def payments(request):
    if request.user.is_authenticated:
        return render(request, 'payments.html', {})

def vehicles(request):
    if request.user.is_authenticated:
        return render(request, 'vehicles.html', {})

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