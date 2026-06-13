from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Wing(models.Model):
    WING_CHOICES = [('A', 'Wing A'), ('B', 'Wing B')]
    name = models.CharField(max_length=1, choices=WING_CHOICES, unique=True)

    def __str__(self):
        return f"Wing {self.name}"


class Floor(models.Model):
    FLOOR_CHOICES = [
        (0, 'Ground Floor'),
        (1, 'First Floor'),
        (2, 'Second Floor'),
        (3, 'Third Floor'),
    ]
    number = models.IntegerField(choices=FLOOR_CHOICES, unique=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    @property
    def room_count(self):
        return 4 if self.number == 0 else 6


class Flat(models.Model):
    flat_number = models.CharField(max_length=10, unique=True)
    wing = models.ForeignKey(Wing, on_delete=models.CASCADE, related_name='flats')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='flats')
    room_number = models.IntegerField()
    monthly_maintenance = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    is_occupied = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['wing__name', 'floor__number', 'room_number']
        unique_together = ['wing', 'floor', 'room_number']

    def __str__(self):
        return self.flat_number

    @property
    def total_balance(self):
        paid = self.payments.filter(
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        due = self.maintenance_dues.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return max(0, due - paid)

    @property
    def payment_status(self):
        balance = self.total_balance
        if balance == 0:
            return 'paid'
        elif balance > 3000:
            return 'overdue'
        return 'pending'


class FlatOwner(models.Model):
    flat = models.OneToOneField(Flat, on_delete=models.CASCADE, related_name='owner')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    move_in_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.flat.flat_number}"


class MaintenanceDue(models.Model):
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='maintenance_dues')
    month = models.IntegerField()   # 1-12
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['flat', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.flat.flat_number} - {self.month}/{self.year}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    ]

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='cash')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='received_payments'
    )
    maintenance_dues = models.ManyToManyField(
        MaintenanceDue, blank=True, related_name='payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"{self.flat.flat_number} - ₹{self.amount} on {self.payment_date}"


class MaintenanceNotice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
