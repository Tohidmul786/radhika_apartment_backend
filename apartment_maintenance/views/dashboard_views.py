from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from apartment_maintenance.models import Flat, Payment


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        flats = list(Flat.objects.select_related('wing', 'floor', 'owner').prefetch_related(
            'payments', 'maintenance_dues'
        ).all())

        paid = [f for f in flats if f.payment_status == 'paid']
        pending = [f for f in flats if f.payment_status == 'pending']
        overdue = [f for f in flats if f.payment_status == 'overdue']

        total_outstanding = sum(f.total_balance for f in flats)
        wing_a_balance = sum(f.total_balance for f in flats if f.wing.name == 'A')
        wing_b_balance = sum(f.total_balance for f in flats if f.wing.name == 'B')

        monthly_collected = Payment.objects.filter(
            payment_date__month=today.month,
            payment_date__year=today.year,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Per-floor breakdown
        floor_breakdown = {}
        for flat in flats:
            key = flat.floor.name
            if key not in floor_breakdown:
                floor_breakdown[key] = {'paid': 0, 'pending': 0, 'overdue': 0, 'balance': 0}
            floor_breakdown[key][flat.payment_status] += 1
            floor_breakdown[key]['balance'] += float(flat.total_balance)

        return Response({
            'total_flats': len(flats),
            'occupied_flats': sum(1 for f in flats if f.is_occupied),
            'paid_count': len(paid),
            'pending_count': len(pending),
            'overdue_count': len(overdue),
            'total_outstanding': total_outstanding,
            'total_collected_this_month': monthly_collected,
            'wing_a_balance': wing_a_balance,
            'wing_b_balance': wing_b_balance,
            'floor_breakdown': floor_breakdown,
        })
