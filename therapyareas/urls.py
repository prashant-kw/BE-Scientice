from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TherapyAreaViewSet

router = DefaultRouter()
router.register(r'', TherapyAreaViewSet, basename='therapy-area')

urlpatterns = [
    path('', include(router.urls)),
]
