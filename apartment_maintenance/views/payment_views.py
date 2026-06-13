from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Sum, Q
from apartment_maintenance.models import Payment, MaintenanceDue, Flat
from apartment_maintenance.serializers import (
    PaymentSerializer, PaymentCreateSerializer, MaintenanceDueSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('flat', 'flat__owner', 'received_by').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        flat_id = self.request.query_params.get('flat')
        wing = self.request.query_params.get('wing')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        payment_mode = self.request.query_params.get('mode')

        if flat_id:
            qs = qs.filter(flat_id=flat_id)
        if wing:
            qs = qs.filter(flat__wing__name=wing.upper())
        if month:
            qs = qs.filter(payment_date__month=month)
        if year:
            qs = qs.filter(payment_date__year=year)
        if payment_mode:
            qs = qs.filter(payment_mode=payment_mode)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(received_by=request.user)

            # Auto mark dues as paid if covered
            flat = payment.flat
            paid_dues = request.data.get('maintenance_dues', [])
            if paid_dues:
                MaintenanceDue.objects.filter(id__in=paid_dues).update(is_paid=True)

            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        today = timezone.now().date()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        monthly = Payment.objects.filter(
            payment_date__month=month,
            payment_date__year=year,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_all = Payment.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'month': month,
            'year': year,
            'monthly_collected': monthly,
            'total_collected': total_all,
        })


class MaintenanceDueViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceDue.objects.select_related('flat', 'flat__owner').all()
    serializer_class = MaintenanceDueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        flat_id = self.request.query_params.get('flat')
        is_paid = self.request.query_params.get('is_paid')
        wing = self.request.query_params.get('wing')

        if flat_id:
            qs = qs.filter(flat_id=flat_id)
        if is_paid is not None:
            qs = qs.filter(is_paid=is_paid.lower() == 'true')
        if wing:
            qs = qs.filter(flat__wing__name=wing.upper())
        return qs

    @action(detail=False, methods=['post'], url_path='generate-monthly')
    def generate_monthly(self, request):
        """Generate maintenance dues for all flats for a given month/year."""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        month = request.data.get('month')
        year = request.data.get('year')
        if not month or not year:
            return Response({'error': 'Month and year are required.'}, status=status.HTTP_400_BAD_REQUEST)

        import datetime
        due_date = datetime.date(int(year), int(month), 10)
        flats = Flat.objects.filter(is_occupied=True).select_related('floor')
        created = 0
        skipped = 0

        for flat in flats:
            _, created_flag = MaintenanceDue.objects.get_or_create(
                flat=flat, month=month, year=year,
                defaults={
                    'amount': flat.monthly_maintenance,
                    'due_date': due_date,
                    'is_paid': False,
                }
            )
            if created_flag:
                created += 1
            else:
                skipped += 1

        return Response({
            'message': f'Dues generated: {created} created, {skipped} already existed.',
            'created': created,
            'skipped': skipped,
        })
