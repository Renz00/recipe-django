from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Reference the health_check view from core/views.py
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health-check/', core_views.health_check, name='health-check'),
    # This will generate a schema file for the API documentation
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='api-schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='api-schema'
        ),
        name='api-docs'
    ),
    path('api/user/', include('user.urls')),
    path('api/recipe/', include('recipe.urls')),
]

# Set to serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )