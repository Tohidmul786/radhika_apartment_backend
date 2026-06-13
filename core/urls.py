from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from apartment_maintenance.views.auth_views import LoginView, LogoutView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth endpoints
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', MeView.as_view(), name='me'),

    # Main app endpoints
    path('api/', include('apartment_maintenance.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
