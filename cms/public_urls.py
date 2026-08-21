from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VideoBulletinPublicViewSet, VideoBulletinLeadCreateView

router = DefaultRouter()
router.register(r'', VideoBulletinPublicViewSet, basename='video-report')

urlpatterns = [
    path('subscribe/', VideoBulletinLeadCreateView.as_view(), name='video-report-subscribe'),
    path('', include(router.urls)),
]
