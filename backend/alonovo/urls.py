from django.contrib import admin
from django.urls import path, include
from core.admin_views import data_guide_view
from core.browse import browse_site

urlpatterns = [
    path('admin/data-guide/', data_guide_view, name='data-guide'),
    path('admin/browse/', browse_site.urls),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
]
