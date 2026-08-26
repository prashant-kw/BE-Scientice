from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuidelineViewSet, ConferenceSocietyViewSet

router = DefaultRouter()
router.register(r'societies', ConferenceSocietyViewSet, basename='conference-societies')
router.register(r'', GuidelineViewSet, basename='guideline')

urlpatterns = [
    path('', include(router.urls)),
]

