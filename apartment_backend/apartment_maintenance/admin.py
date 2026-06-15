from django.contrib import admin
from .models import Wing, Floor, Flat, FlatOwner, MaintenanceDue, Payment, MaintenanceNotice


@admin.register(Wing)
class WingAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'room_count']


class FlatOwnerInline(admin.StackedInline):
    model = FlatOwner
    extra = 0
    can_delete = False


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ['flat_number', 'wing', 'floor', 'room_number', 'monthly_maintenance', 'is_occupied', 'payment_status', 'total_balance']
    list_filter = ['wing', 'floor', 'is_occupied']
    search_fields = ['flat_number', 'owner__name', 'owner__phone']
    inlines = [FlatOwnerInline]
    readonly_fields = ['flat_number', 'payment_status', 'total_balance']


@admin.register(FlatOwner)
class FlatOwnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'flat', 'phone', 'email', 'is_active', 'move_in_date']
    search_fields = ['name', 'phone', 'email', 'flat__flat_number']
    list_filter = ['is_active']


@admin.register(MaintenanceDue)
class MaintenanceDueAdmin(admin.ModelAdmin):
    list_display = ['flat', 'month', 'year', 'amount', 'due_date', 'is_paid']
    list_filter = ['year', 'month', 'is_paid', 'flat__wing']
    search_fields = ['flat__flat_number', 'flat__owner__name']
    list_editable = ['is_paid']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['flat', 'amount', 'payment_date', 'payment_mode', 'status', 'received_by']
    list_filter = ['status', 'payment_mode', 'payment_date', 'flat__wing']
    search_fields = ['flat__flat_number', 'flat__owner__name', 'transaction_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'payment_date'


@admin.register(MaintenanceNotice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active']
