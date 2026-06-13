from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from apartment_maintenance.models import Flat, FlatOwner, Wing, Floor
from apartment_maintenance.serializers import (
    FlatListSerializer, FlatDetailSerializer, FlatCreateUpdateSerializer,
    FlatOwnerSerializer, WingSerializer, FloorSerializer
)


class WingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Wing.objects.all()
    serializer_class = WingSerializer
    permission_classes = [IsAuthenticated]


class FloorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer
    permission_classes = [IsAuthenticated]


class FlatViewSet(viewsets.ModelViewSet):
    queryset = Flat.objects.select_related('wing', 'floor', 'owner').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return FlatListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FlatCreateUpdateSerializer
        return FlatDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        wing = self.request.query_params.get('wing')
        floor = self.request.query_params.get('floor')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if wing:
            qs = qs.filter(wing__name=wing.upper())
        if floor is not None:
            qs = qs.filter(floor__number=floor)
        if search:
            qs = qs.filter(
                Q(flat_number__icontains=search) |
                Q(owner__name__icontains=search) |
                Q(owner__phone__icontains=search)
            )
        return qs

    def filter_by_status(self, queryset, status_filter):
        result = []
        for flat in queryset:
            if flat.payment_status == status_filter:
                result.append(flat.id)
        return queryset.filter(id__in=result)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        status_filter = request.query_params.get('status')
        if status_filter in ['paid', 'pending', 'overdue']:
            qs = self.filter_by_status(qs, status_filter)
        serializer = FlatListSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = FlatCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            wing = serializer.validated_data['wing']
            floor = serializer.validated_data['floor']
            room_number = serializer.validated_data['room_number']
            flat_number = f"{wing.name}-{floor.name[0]}{room_number}"
            flat = serializer.save(flat_number=flat_number)
            return Response(FlatDetailSerializer(flat).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlatOwnerViewSet(viewsets.ModelViewSet):
    queryset = FlatOwner.objects.select_related('flat').all()
    serializer_class = FlatOwnerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        flat_id = self.request.query_params.get('flat')
        if flat_id:
            qs = qs.filter(flat_id=flat_id)
        return qs

    def create(self, request, *args, **kwargs):
        flat_id = request.data.get('flat')
        if FlatOwner.objects.filter(flat_id=flat_id).exists():
            return Response(
                {'error': 'This flat already has an owner. Update instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
