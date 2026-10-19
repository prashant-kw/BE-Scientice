from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuidelineViewSet, ConferenceSocietyViewSet, proxy_pdf_view

router = DefaultRouter()
router.register(r'societies', ConferenceSocietyViewSet, basename='conference-societies')
router.register(r'', GuidelineViewSet, basename='guideline')

urlpatterns = [
    path('proxy-pdf/', proxy_pdf_view, name='guideline-proxy-pdf'),
    path('', include(router.urls)),
]

