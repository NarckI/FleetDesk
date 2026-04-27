from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    #drivers
    path('drivers/', views.drivers, name='drivers'),
    path('drivers/add/', views.driver_add, name='driver_add'),
    path('drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    path('drivers/<int:pk>/data/', views.driver_data_json, name='driver_data_json'),

    path('repairs/', views.repairs, name='repairs'),
    path('payments/', views.payments, name='payments'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('contracts/', views.contracts, name='contracts'),
    path('notifications/', views.notifications, name='notifications'),
]
