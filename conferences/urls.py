from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConferenceViewSet

router = DefaultRouter()
router.register(r'', ConferenceViewSet, basename='conference')

urlpatterns = [
    path('', include(router.urls)),
]
