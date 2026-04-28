from django.db import models
from datetime import date

# Driver
class Driver(models.Model):
    STATUS_CHOICES = [('active','Active'),('inactive','Inactive'),('suspended','Suspended')]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    license_expiry = models.DateField()
    date_joined = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name','first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def has_active_contract(self):
        return self.contracts.filter(status='active').exists()

#Vehicles
class Vehicle(models.Model):
    STATUS_CHOICES = [('available','Available'),('in-use','In Use'),('maintenance','Maintenance')]
    TYPE_CHOICES = [('4-seater','4 Seater'),('7-seater','7 Seater')]

    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_registration = models.CharField(max_length=100, blank=True)
    or_expiry = models.DateField(null=True, blank=True)
    cr_expiry = models.DateField(null=True, blank=True)
    cpc_expiry = models.DateField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField(default=0)
    last_maintenance = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['plate_number']

    def __str__(self):
        return f"{self.plate_number} - {self.brand} {self.model}"

#Contracts
class Contract(models.Model):
    STATUS_CHOICES = [('active','Active'),('expired','Expired'),('terminated','Terminated')]
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='contracts')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='contracts')
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract #{self.pk} — {self.driver}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'active':
            self.vehicle.status = 'in-use'
            self.vehicle.save(update_fields=['status'])
        elif self.status in ('expired','terminated'):
            still_active = Contract.objects.filter(vehicle=self.vehicle, status='active').exclude(pk=self.pk).exists()
            if not still_active:
                self.vehicle.status = 'available'
                self.vehicle.save(update_fields=['status'])

#Repair
class Repair(models.Model):
    pass