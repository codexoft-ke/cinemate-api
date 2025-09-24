"""cinemate URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API endpoints
    path('auth/', include('apps.authentication.urls')),
    path('movies/', include('apps.movies.urls')),
    path('profile/', include('apps.users.urls')),
    path('system/', include('apps.common.urls')),
]