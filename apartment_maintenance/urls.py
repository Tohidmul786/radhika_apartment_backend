from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apartment_maintenance.views.flat_views import FlatViewSet, FlatOwnerViewSet, WingViewSet, FloorViewSet
from apartment_maintenance.views.payment_views import PaymentViewSet, MaintenanceDueViewSet
from apartment_maintenance.views.dashboard_views import DashboardView
from apartment_maintenance.views.report_views import ExportPDFView, ExportExcelView, FlatReceiptPDFView
<<<<<<< HEAD
from apartment_maintenance.views.email_views import SendOverdueRemindersView, SendSingleReminderView, TestEmailView
=======
from apartment_maintenance.views.email_views import SendOverdueRemindersView, SendSingleReminderView
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d

router = DefaultRouter()
router.register(r'wings',    WingViewSet)
router.register(r'floors',   FloorViewSet)
router.register(r'flats',    FlatViewSet)
router.register(r'owners',   FlatOwnerViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'dues',     MaintenanceDueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/',                          DashboardView.as_view(),      name='dashboard'),
    path('reports/pdf/',                        ExportPDFView.as_view(),       name='export-pdf'),
    path('reports/excel/',                      ExportExcelView.as_view(),     name='export-excel'),
    path('reports/receipt/<str:flat_number>/',  FlatReceiptPDFView.as_view(),  name='flat-receipt'),
    path('reminders/send-overdue/',             SendOverdueRemindersView.as_view(), name='send-overdue-reminders'),
    path('reminders/send/<str:flat_number>/',   SendSingleReminderView.as_view(),  name='send-single-reminder'),
<<<<<<< HEAD
    path('reminders/test-email/',               TestEmailView.as_view(),           name='test-email'),
=======
>>>>>>> 481a7b532f58ab961653c399463a46333b3f184d
]
