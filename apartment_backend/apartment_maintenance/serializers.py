from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Wing, Floor, Flat, FlatOwner, MaintenanceDue, Payment, MaintenanceNotice


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


class WingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wing
        fields = '__all__'


class FloorSerializer(serializers.ModelSerializer):
    room_count = serializers.ReadOnlyField()

    class Meta:
        model = Floor
        fields = '__all__'


class FlatOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatOwner
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class FlatOwnerInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatOwner
        fields = ['name', 'phone', 'email', 'move_in_date']


class MaintenanceDueSerializer(serializers.ModelSerializer):
    flat_number = serializers.CharField(source='flat.flat_number', read_only=True)

    class Meta:
        model = MaintenanceDue
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    flat_number = serializers.CharField(source='flat.flat_number', read_only=True)
    owner_name = serializers.CharField(source='flat.owner.name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'received_by']


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['flat', 'amount', 'payment_date', 'payment_mode', 'transaction_id', 'notes', 'maintenance_dues']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class FlatListSerializer(serializers.ModelSerializer):
    wing_name = serializers.CharField(source='wing.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    floor_number = serializers.IntegerField(source='floor.number', read_only=True)
    owner = FlatOwnerInlineSerializer(read_only=True)
    total_balance = serializers.ReadOnlyField()
    payment_status = serializers.ReadOnlyField()

    class Meta:
        model = Flat
        fields = [
            'id', 'flat_number', 'wing_name', 'floor_name', 'floor_number',
            'room_number', 'monthly_maintenance', 'is_occupied',
            'owner', 'total_balance', 'payment_status'
        ]


class FlatDetailSerializer(serializers.ModelSerializer):
    wing = WingSerializer(read_only=True)
    floor = FloorSerializer(read_only=True)
    owner = FlatOwnerSerializer(read_only=True)
    total_balance = serializers.ReadOnlyField()
    payment_status = serializers.ReadOnlyField()
    recent_payments = serializers.SerializerMethodField()
    pending_dues = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = '__all__'

    def get_recent_payments(self, obj):
        payments = obj.payments.filter(status='completed').order_by('-payment_date')[:5]
        return PaymentSerializer(payments, many=True).data

    def get_pending_dues(self, obj):
        dues = obj.maintenance_dues.filter(is_paid=False).order_by('-year', '-month')
        return MaintenanceDueSerializer(dues, many=True).data


class FlatCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ['wing', 'floor', 'room_number', 'monthly_maintenance', 'is_occupied']

    def validate(self, data):
        wing = data.get('wing')
        floor = data.get('floor')
        room_number = data.get('room_number')
        # A Wing: Ground=2, upper floors=5
        # B Wing: Ground=4, upper floors=6
        if wing.name == 'A':
            max_rooms = 2 if floor.number == 0 else 5
        else:
            max_rooms = 4 if floor.number == 0 else 6
        if room_number < 1 or room_number > max_rooms:
            raise serializers.ValidationError(
                f"Room number must be between 1 and {max_rooms} for Wing {wing.name} {floor.name}."
            )
        return data


class DashboardStatsSerializer(serializers.Serializer):
    total_flats = serializers.IntegerField()
    occupied_flats = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_collected_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    wing_a_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    wing_b_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
