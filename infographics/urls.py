from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InfographicViewSet

router = DefaultRouter()
router.register(r'', InfographicViewSet, basename='infographic')

urlpatterns = [
    path('', include(router.urls)),
]
