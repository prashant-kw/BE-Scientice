from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticleCMSViewSet,
    GuidelineCMSViewSet,
    ConferenceCMSViewSet,
    EducationResourceCMSViewSet,
    InfographicCMSViewSet,
    TherapyAreaCMSViewSet,
    SiteInfoCMSView,
    ContactMessageCMSViewSet,
    UserCMSViewSet,
    CMSStatsView,
    PageCMSViewSet,
    PagePublicViewSet,
)

router = DefaultRouter()
router.register(r'articles', ArticleCMSViewSet, basename='cms-articles')
router.register(r'guidelines', GuidelineCMSViewSet, basename='cms-guidelines')
router.register(r'conferences', ConferenceCMSViewSet, basename='cms-conferences')
router.register(r'education', EducationResourceCMSViewSet, basename='cms-education')
router.register(r'infographics', InfographicCMSViewSet, basename='cms-infographics')
router.register(r'therapy-areas', TherapyAreaCMSViewSet, basename='cms-therapy-areas')
router.register(r'messages', ContactMessageCMSViewSet, basename='cms-messages')
router.register(r'users', UserCMSViewSet, basename='cms-users')
router.register(r'pages', PageCMSViewSet, basename='cms-pages')
router.register(r'public-pages', PagePublicViewSet, basename='public-pages')

urlpatterns = [
    path('stats/', CMSStatsView.as_view(), name='cms-stats'),
    path('site-info/', SiteInfoCMSView.as_view(), name='cms-site-info'),
    path('', include(router.urls)),
]
