from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PagePublicViewSet

router = DefaultRouter()
router.register(r'', PagePublicViewSet, basename='public-page')

urlpatterns = [
    path('', include(router.urls)),
]
