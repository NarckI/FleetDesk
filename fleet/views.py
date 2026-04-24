from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

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
            messages.success(request, 'You are now logged in')
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')
    return render(request,'login.html', {})

def logout_user(request):
    logout(request)
    return redirect('login')

def driver(request):
    if request.user.is_authenticated:
        return redirect('driver')

def repairs(request):
    if request.user.is_authenticated:
        return redirect('repairs')

def payments(request):
    if request.user.is_authenticated:
        return redirect('payments')

def vehicles(request):
    if request.user.is_authenticated:
        return redirect('vehicles')

def contracts(request):
    if request.user.is_authenticated:
        return redirect('contracts')