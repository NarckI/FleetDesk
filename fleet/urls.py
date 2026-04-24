from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('driver/', views.driver, name='driver'),
    path('repairs/', views.repairs, name='repairs'),
    path('payments/', views.payments, name='payments'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('contracts/', views.contracts, name='contracts'),
]
