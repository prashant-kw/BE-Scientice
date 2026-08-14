"""
URL Configuration for Scientice project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Custom Admin Site Branding
admin.site.site_header = "Scientice Content Management"
admin.site.site_title = "Scientice Admin"
admin.site.index_title = "Scientice Portal Administration"

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation (Swagger & OpenAPI Schema)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Application API Routes
    path('api/auth/', include('accounts.urls')),
    path('api/news/', include('news.urls')),
    path('api/therapy-areas/', include('therapyareas.urls')),
    path('api/conferences/', include('conferences.urls')),
    path('api/education/', include('education.urls')),
    path('api/guidelines/', include('guidelines.urls')),
    path('api/infographics/', include('infographics.urls')),
    path('api/', include('sitecontact.urls')),
    path('api/cms/', include('cms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
