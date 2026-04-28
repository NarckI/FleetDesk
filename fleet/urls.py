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

    # Vehicles
    path('vehicles/', views.vehicles, name='vehicles'),
    path('vehicles/add/', views.vehicle_add, name='vehicle_add'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicles/<int:pk>/data/', views.vehicle_data_json, name='vehicle_data_json'),
    path('vehicles/<int:pk>/repair/', views.vehicle_create_repair, name='vehicle_create_repair'),

    # Contracts
    path('contracts/', views.contracts, name='contracts'),
    path('contracts/add/', views.contract_add, name='contract_add'),
    path('contracts/<int:pk>/edit/', views.contract_edit, name='contract_edit'),
    path('contracts/<int:pk>/delete/', views.contract_delete, name='contract_delete'),
    path('contracts/<int:pk>/data/', views.contract_data_json, name='contract_data_json'),
    path('contracts/drivers/', views.contract_drivers_json, name='contract_drivers_json'),
    path('contracts/vehicles/', views.contract_vehicles_json, name='contract_vehicles_json'),

    # Payments
    path('payments/', views.payments, name='payments'),
    path('payments/<int:pk>/mark-paid/', views.payment_mark_paid, name='payment_mark_paid'),
    path('payments/<int:pk>/partial/', views.payment_partial, name='payment_partial'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    # Repairs
    path('repairs/', views.repairs, name='repairs'),
    path('repairs/<int:pk>/save/', views.repair_save_details, name='repair_save_details'),
    path('repairs/<int:pk>/complete/', views.repair_mark_completed, name='repair_mark_completed'),
    path('repairs/<int:pk>/delete/', views.repair_delete, name='repair_delete'),
    path('repairs/<int:pk>/detail/', views.repair_detail_json, name='repair_detail_json'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),
]
