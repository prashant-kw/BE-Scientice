from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticleCMSViewSet,
    GuidelineCMSViewSet,
    ConferenceCMSViewSet,
    EducationCategoryCMSViewSet,
    EducationResourceCMSViewSet,
    InfographicCMSViewSet,
    TherapyAreaCMSViewSet,
    SiteInfoCMSView,
    ContactMessageCMSViewSet,
    UserCMSViewSet,
    CMSStatsView,
    PageCMSViewSet,
    PagePublicViewSet,
    VideoBulletinCMSViewSet,
    VideoBulletinLeadCMSViewSet,
    KeyHighlightItemCMSViewSet,
    KeyHighlightItemPublicViewSet,
    ConferenceSocietyCMSViewSet,
    ConferenceCategoryCMSViewSet,
    ContentSectionVisibilityCMSViewSet,
    ContentSectionPublicView,
    CMSFileUploadView,
)


router = DefaultRouter()
router.register(r'articles', ArticleCMSViewSet, basename='cms-articles')
router.register(r'guidelines', GuidelineCMSViewSet, basename='cms-guidelines')
router.register(r'societies', ConferenceSocietyCMSViewSet, basename='cms-societies')
router.register(r'conferences', ConferenceCMSViewSet, basename='cms-conferences')
router.register(r'conference-categories', ConferenceCategoryCMSViewSet, basename='cms-conference-categories')
router.register(r'education-categories', EducationCategoryCMSViewSet, basename='cms-education-categories')
router.register(r'education', EducationResourceCMSViewSet, basename='cms-education')
router.register(r'infographics', InfographicCMSViewSet, basename='cms-infographics')
router.register(r'therapy-areas', TherapyAreaCMSViewSet, basename='cms-therapy-areas')
router.register(r'section-visibility', ContentSectionVisibilityCMSViewSet, basename='cms-section-visibility')
router.register(r'messages', ContactMessageCMSViewSet, basename='cms-messages')
router.register(r'users', UserCMSViewSet, basename='cms-users')
router.register(r'pages', PageCMSViewSet, basename='cms-pages')
router.register(r'public-pages', PagePublicViewSet, basename='public-pages')
router.register(r'video-bulletins', VideoBulletinCMSViewSet, basename='cms-video-bulletins')
router.register(r'video-bulletin-leads', VideoBulletinLeadCMSViewSet, basename='cms-video-bulletin-leads')
router.register(r'key-highlights', KeyHighlightItemCMSViewSet, basename='cms-key-highlights')
router.register(r'public-key-highlights', KeyHighlightItemPublicViewSet, basename='public-key-highlights')


urlpatterns = [
    path('stats/', CMSStatsView.as_view(), name='cms-stats'),
    path('site-info/', SiteInfoCMSView.as_view(), name='cms-site-info'),
    path('sections/public/', ContentSectionPublicView.as_view(), name='public-section-visibility'),
    path('sections/live-counts/', ContentSectionPublicView.as_view(), name='cms-section-live-counts'),
    path('upload/', CMSFileUploadView.as_view(), name='cms-file-upload'),
    path('', include(router.urls)),
]
