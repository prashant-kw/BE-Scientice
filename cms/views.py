import csv
from django.db import models
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, generics, permissions, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


class CMSPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


from common.permissions import IsContentEditor

from common.throttling import ContactSubmissionRateThrottle

from accounts.models import User
from news.models import Article
from guidelines.models import Guideline, ConferenceSociety
from conferences.models import Conference, ConferenceRegistration, ConferenceCategory
from education.models import EducationResource, EducationCategory
from infographics.models import Infographic
from therapyareas.models import TherapyArea
from sitecontact.models import SiteInfo, ContactMessage
from cms.models import VideoBulletinLead, ContentSectionVisibility, Page, VideoBulletin, VideoGenerationJob, KeyHighlightItem
from .serializers import (
    ArticleCMSSerializer,
    GuidelineCMSSerializer,
    ConferenceCMSSerializer,
    ConferenceRegistrationCMSListSerializer,
    ConferenceCategoryCMSSerializer,
    EducationCategoryCMSSerializer,
    EducationResourceCMSSerializer,
    InfographicCMSSerializer,
    TherapyAreaCMSSerializer,
    SiteInfoCMSSerializer,
    ContactMessageCMSReadSerializer,
    UserCMSListSerializer,
    PageCMSSerializer,
    PagePublicSerializer,
    VideoBulletinListSerializer,
    VideoBulletinSerializer,
    VideoBulletinPublicSerializer,
    VideoBulletinLeadSerializer,
    VideoGenerationJobSerializer,
    ContentSectionVisibilitySerializer,
    ContentSectionPublicSerializer,
    ConferenceSocietyCMSSerializer,
    KeyHighlightItemSerializer,
)

# ----------------------------------------------------------------------
# 1. Article CMS ViewSet
# ----------------------------------------------------------------------
class ArticleCMSViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().select_related('category')
    serializer_class = ArticleCMSSerializer
    permission_classes = [IsContentEditor]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['is_published', 'is_headline', 'category']
    search_fields = ['title', 'summary', 'body', 'reference_name', 'category_name_override']
    ordering_fields = ['published_at', 'created_at', 'title', 'is_published']
    ordering = ['-published_at', '-created_at']

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        article = self.get_object()
        article.is_published = not article.is_published
        article.save()
        return Response({'id': article.id, 'is_published': article.is_published})

# ----------------------------------------------------------------------
# 2. Guideline CMS ViewSet
# ----------------------------------------------------------------------
class GuidelineCMSViewSet(viewsets.ModelViewSet):
    queryset = Guideline.objects.all().select_related('category')
    serializer_class = GuidelineCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'category', 'authority']
    search_fields = ['title', 'authority', 'summary', 'category_name_override']
    ordering_fields = ['published_at', 'created_at', 'title', 'is_published']
    ordering = ['-published_at']

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        guideline = self.get_object()
        guideline.is_published = not guideline.is_published
        guideline.save()
        return Response({'id': guideline.id, 'is_published': guideline.is_published})

# ----------------------------------------------------------------------
# 3. Conference CMS ViewSet & Registrations
# ----------------------------------------------------------------------
class ConferenceCMSViewSet(viewsets.ModelViewSet):
    queryset = Conference.objects.all().select_related('category').prefetch_related('registrations')
    serializer_class = ConferenceCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'category', 'is_virtual_available']
    search_fields = ['title', 'description', 'location', 'category_name_override']
    ordering_fields = ['start_date', 'title', 'created_at', 'is_published']
    ordering = ['-start_date']

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        conference = self.get_object()
        conference.is_published = not conference.is_published
        conference.save()
        return Response({'id': conference.id, 'is_published': conference.is_published})

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        """
        List all registrations for this specific conference.
        """
        conference = self.get_object()
        regs = conference.registrations.all().order_by('-registered_at')
        serializer = ConferenceRegistrationCMSListSerializer(regs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def export_registrations(self, request, pk=None):
        """
        Stream conference attendee registrations as a downloadable CSV file.
        """
        conference = self.get_object()
        regs = conference.registrations.all().order_by('-registered_at')

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        safe_slug = conference.slug or f"conf_{conference.id}"
        response['Content-Disposition'] = f'attachment; filename="{safe_slug}_registrations.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Full Name', 'Email', 'Attendance Mode', 'Organization', 'Registered At (UTC)'])

        for reg in regs:
            writer.writerow([
                reg.id,
                reg.full_name,
                reg.email,
                reg.get_attendance_mode_display(),
                reg.organization,
                reg.registered_at.strftime('%Y-%m-%d %H:%M:%S') if reg.registered_at else '',
            ])

        return response

# ----------------------------------------------------------------------
# 4. Education Category & Resource CMS ViewSets
# ----------------------------------------------------------------------
class EducationCategoryCMSViewSet(viewsets.ModelViewSet):
    queryset = EducationCategory.objects.all().prefetch_related('resources')
    serializer_class = EducationCategoryCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'key']
    search_fields = ['title', 'description', 'key']
    ordering_fields = ['order', 'id', 'title', 'is_active', 'created_at']
    ordering = ['order', 'id']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        cat = self.get_object()
        cat.is_active = not cat.is_active
        cat.save(update_fields=['is_active', 'updated_at'])
        return Response({'id': cat.id, 'key': cat.key, 'is_active': cat.is_active})

class EducationResourceCMSViewSet(viewsets.ModelViewSet):
    queryset = EducationResource.objects.all().select_related('category')
    serializer_class = EducationResourceCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'category']
    search_fields = ['title', 'description', 'body']
    ordering_fields = ['published_at', 'created_at', 'title', 'is_published']
    ordering = ['-published_at']

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        res = self.get_object()
        res.is_published = not res.is_published
        res.save()
        return Response({'id': res.id, 'is_published': res.is_published})

# ----------------------------------------------------------------------
# 5. Infographic CMS ViewSet (with nested atomic points)
# ----------------------------------------------------------------------
class InfographicCMSViewSet(viewsets.ModelViewSet):
    queryset = Infographic.objects.all().prefetch_related('points')
    serializer_class = InfographicCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'category']
    search_fields = ['title', 'subtitle', 'quote', 'alert', 'reference']
    ordering_fields = ['published_at', 'created_at', 'title', 'is_published']
    ordering = ['-published_at', '-created_at']

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        info = self.get_object()
        info.is_published = not info.is_published
        info.save()
        return Response({'id': info.id, 'is_published': info.is_published})

# ----------------------------------------------------------------------
# 6. Therapy Area CMS ViewSet
# ----------------------------------------------------------------------
class TherapyAreaCMSViewSet(viewsets.ModelViewSet):
    queryset = TherapyArea.objects.all()
    serializer_class = TherapyAreaCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        ta = self.get_object()
        ta.is_active = not ta.is_active
        ta.save(update_fields=['is_active', 'updated_at'])
        return Response({'id': ta.id, 'name': ta.name, 'is_active': ta.is_active})

# ----------------------------------------------------------------------
# 7. SiteInfo CMS View (Singleton Retrieve/Update - No POST/DELETE)
# ----------------------------------------------------------------------
class SiteInfoCMSView(generics.RetrieveUpdateAPIView):
    serializer_class = SiteInfoCMSSerializer
    permission_classes = [IsContentEditor]

    def get_object(self):
        # Strict solo singleton guarantee — no URL pk parameter accepted
        return SiteInfo.get_solo()

# ----------------------------------------------------------------------
# 8. ContactMessage CMS ViewSet (Read & Mark-as-read Only)
# ----------------------------------------------------------------------
class ContactMessageCMSViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    http_method_names = ['get', 'patch', 'post', 'head', 'options']
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageCMSReadSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_read']
    search_fields = ['name', 'email', 'subject', 'message']

    @action(detail=True, methods=['post'])
    def toggle_read(self, request, pk=None):
        msg = self.get_object()
        msg.is_read = not msg.is_read
        msg.save()
        return Response({'id': msg.id, 'is_read': msg.is_read})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        updated_count = ContactMessage.objects.filter(is_read=False).update(is_read=True)
        return Response({'updated': updated_count, 'message': f'{updated_count} messages marked as read.'})

# ----------------------------------------------------------------------
# 9. Registered Users CMS ViewSet (Healthcare Professionals & Members)
# ----------------------------------------------------------------------
class UserCMSViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    View, filter, verify credentials, and manage registered healthcare professionals.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserCMSListSerializer
    permission_classes = [IsContentEditor]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['role', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['email', 'full_name', 'specialty', 'license_number', 'city', 'state']
    ordering_fields = ['date_joined', 'last_login', 'full_name', 'email', 'role']
    ordering = ['-date_joined']

    @action(detail=True, methods=['post'])
    def toggle_verified(self, request, pk=None):
        user = self.get_object()
        user.is_verified = not user.is_verified
        user.save(update_fields=['is_verified'])
        return Response({
            'id': user.id,
            'is_verified': user.is_verified,
            'isVerified': user.is_verified,
            'message': f"User {user.full_name or user.email} verification status changed to {user.is_verified}."
        })

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        if user == request.user and user.is_superuser:
            return Response({'error': 'Cannot deactivate your own superuser account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({
            'id': user.id,
            'is_active': user.is_active,
            'isActive': user.is_active,
            'message': f"User {user.full_name or user.email} active status changed to {user.is_active}."
        })

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="scientice_registered_users.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'Full Name', 'Role', 'Specialty', 'License / Reg No', 'City', 'State', 'Verified', 'Active', 'Staff', 'Date Joined', 'Last Login'])
        
        users = self.filter_queryset(self.get_queryset())
        for u in users:
            writer.writerow([
                u.id,
                u.email,
                u.full_name,
                u.get_role_display(),
                u.specialty,
                u.license_number,
                u.city,
                u.state,
                'Yes' if u.is_verified else 'No',
                'Yes' if u.is_active else 'No',
                'Yes' if u.is_staff else 'No',
                u.date_joined.strftime('%Y-%m-%d %H:%M') if u.date_joined else '',
                u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else 'Never',
            ])
        return response

# ----------------------------------------------------------------------
# 10. CMS Dashboard Overview Stats View
# ----------------------------------------------------------------------
class CMSStatsView(APIView):
    permission_classes = [IsContentEditor]

    def get(self, request):
        now = timezone.now().date()
        stats = {
            'articles_total': Article.objects.count(),
            'articles_published': Article.objects.filter(is_published=True).count(),
            'guidelines_total': Guideline.objects.count(),
            'conferences_total': Conference.objects.count(),
            'conferences_upcoming': Conference.objects.filter(end_date__gte=now).count(),
            'registrations_total': ConferenceRegistration.objects.count(),
            'infographics_total': Infographic.objects.count(),
            'education_total': EducationResource.objects.count(),
            'therapy_areas_total': TherapyArea.objects.count(),
            'video_bulletins_total': VideoBulletin.objects.count(),
            'video_bulletins_published': VideoBulletin.objects.filter(is_published=True).count(),
            'messages_unread': ContactMessage.objects.filter(is_read=False).count(),
            'messages_total': ContactMessage.objects.count(),
            'users_total': User.objects.count(),
            'users_verified': User.objects.filter(is_verified=True).count(),
            'doctors_total': User.objects.filter(role=User.Role.DOCTOR).count(),
            'pages_total': Page.objects.count(),
        }

        return Response(stats)

# ----------------------------------------------------------------------
# 11. Page CMS ViewSet
# ----------------------------------------------------------------------
from .models import Page, VideoBulletin, VideoGenerationJob

class PageCMSViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'content']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['title']

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        page = self.get_object()
        page.is_published = not page.is_published
        page.save()
        return Response({'id': page.id, 'is_published': page.is_published})

# ----------------------------------------------------------------------
# 12. Page Public ViewSet (Read Only, Lookup by Slug)
# ----------------------------------------------------------------------
class PagePublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.filter(is_published=True)
    serializer_class = PagePublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class VideoBulletinCMSViewSet(viewsets.ModelViewSet):
    queryset = VideoBulletin.objects.all().order_by('-published_at', '-created_at')
    serializer_class = VideoBulletinSerializer
    permission_classes = [IsContentEditor]
    pagination_class = CMSPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'script', 'slug']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at', '-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoBulletinListSerializer
        return VideoBulletinSerializer



    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        bulletin = self.get_object()
        bulletin.is_published = not bulletin.is_published
        if bulletin.is_published:
            bulletin.published_at = timezone.now()
        bulletin.save(update_fields=['is_published', 'published_at', 'updated_at'])
        return Response({'id': bulletin.id, 'is_published': bulletin.is_published})


    @action(detail=True, methods=['post'])
    def generate_video(self, request, pk=None):
        bulletin = self.get_object()

        # Protection against accidental API credit consumption
        has_avatar = bool(bulletin.custom_avatar_image or bulletin.avatar in ['female_doctor', 'male_doctor', 'female_anchor', 'male_anchor'])
        has_bg = bool(bulletin.background_image or bulletin.background_image_url)

        if not has_avatar or not has_bg:
            missing = []
            if not has_avatar:
                missing.append('Presenter Avatar Image')
            if not has_bg:
                missing.append('Background Image / URL')
            return Response(
                {
                    'detail': f'Video generation blocked: Please provide mandatory assets ({", ".join(missing)}) before triggering AI video generation.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


        # Cancel any previous/in-progress jobs so every click on Regenerate triggers a 100% fresh audio & video rendering pass
        bulletin.generation_jobs.filter(
            status__in=[VideoGenerationJob.Status.QUEUED, VideoGenerationJob.Status.AUDIO,
                        VideoGenerationJob.Status.AVATAR, VideoGenerationJob.Status.COMPOSING]
        ).update(status=VideoGenerationJob.Status.FAILED, error='Replaced by fresh generation request')

        import uuid
        task_uuid = f'job-{uuid.uuid4().hex[:12]}'
        job = VideoGenerationJob.objects.create(bulletin=bulletin, task_id=task_uuid)
        from .tasks import generate_video_bulletin

        # Dispatch via background thread to guarantee instant HTTP 202 response without Gunicorn worker timeout
        import threading
        t = threading.Thread(target=generate_video_bulletin, args=(job.id,), daemon=True)
        t.start()

        return Response(VideoGenerationJobSerializer(job, context={'request': request}).data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'])
    def generation_status(self, request, pk=None):
        bulletin = self.get_object()
        job = bulletin.generation_jobs.first()
        if not job:
            return Response({'detail': 'No generation job exists.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(VideoGenerationJobSerializer(job, context={'request': request}).data)


class VideoBulletinPublicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VideoBulletinPublicSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = 'slug'

    def get_queryset(self):
        now = timezone.now()
        qs = VideoBulletin.objects.filter(is_published=True)
        if self.action == 'list':
            qs = qs.filter(
                models.Q(schedule_end_datetime__isnull=True) | models.Q(schedule_end_datetime__gte=now)
            )
        return qs.order_by(
            models.F('schedule_start_datetime').desc(nulls_last=True),
            models.F('event_start_datetime').desc(nulls_last=True),
            models.F('launch_datetime').desc(nulls_last=True),
            '-published_at',
            '-created_at'
        )






class VideoBulletinLeadCreateView(generics.CreateAPIView):
    serializer_class = VideoBulletinLeadSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactSubmissionRateThrottle]


class VideoBulletinLeadCMSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VideoBulletinLead.objects.all().order_by('-created_at')
    serializer_class = VideoBulletinLeadSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bulletin', 'profession']
    search_fields = ['mobile', 'name', 'email', 'profession']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bulletin_subscribers.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Mobile Number', 'Name', 'Email', 'Hospital / Institution', 'Profession', 'Interests', 'Submitted At'])

        qs = self.filter_queryset(self.get_queryset())
        for lead in qs:
            interests_str = ', '.join(lead.interests) if isinstance(lead.interests, list) else str(lead.interests)
            writer.writerow([
                lead.id,
                lead.mobile,
                lead.name or '',
                lead.email or '',
                lead.hospital_name or '',
                lead.profession or '',
                interests_str,
                lead.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])


        return response




from .models import KeyHighlightItem
from .serializers import KeyHighlightItemSerializer

class KeyHighlightItemCMSViewSet(viewsets.ModelViewSet):
    queryset = KeyHighlightItem.objects.all()
    serializer_class = KeyHighlightItemSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'category']
    ordering_fields = ['order', 'created_at']
    ordering = ['order', '-created_at']

class KeyHighlightItemPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = KeyHighlightItem.objects.filter(is_published=True)
    serializer_class = KeyHighlightItemSerializer
    permission_classes = [permissions.AllowAny]


from guidelines.models import ConferenceSociety
from .serializers import ConferenceSocietyCMSSerializer

class ConferenceSocietyCMSViewSet(viewsets.ModelViewSet):
    queryset = ConferenceSociety.objects.all()
    serializer_class = ConferenceSocietyCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['order', 'code', 'name', 'created_at']
    ordering = ['order', 'code']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        society = self.get_object()
        society.is_active = not society.is_active
        society.save(update_fields=['is_active', 'updated_at'])
        return Response({'id': society.id, 'is_active': society.is_active})


# ----------------------------------------------------------------------
# Conference Categories / Formats (Subcategory Visibility)
# ----------------------------------------------------------------------
class ConferenceCategoryCMSViewSet(viewsets.ModelViewSet):
    queryset = ConferenceCategory.objects.all()
    serializer_class = ConferenceCategoryCMSSerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        cat = self.get_object()
        cat.is_active = not cat.is_active
        cat.save(update_fields=['is_active', 'updated_at'])
        return Response({'id': cat.id, 'name': cat.name, 'is_active': cat.is_active})


# ----------------------------------------------------------------------
# Universal Section Visibility & Auto-Suppression Views
# ----------------------------------------------------------------------
SECTION_SITE_INFO_MAP = {
    'hero_banner': 'show_hero_banner',
    'guidelines_showcase': 'show_guidelines_showcase',
    'headline_slider': 'show_headline_slider',
    'news_articles': 'show_news_widget',
    'therapy_areas': 'show_therapy_areas_widget',
    'conferences': 'show_conferences_widget',
    'education': 'show_education_widget',
    'guidelines_widget': 'show_guidelines_widget',
}


def get_section_live_counts(section_key):
    """
    Compute live published items count and total items count for any section.
    """
    now = timezone.now()
    try:
        if section_key == 'hero_banner':
            total = VideoBulletin.objects.count()
            published = VideoBulletin.objects.filter(is_published=True).filter(
                models.Q(schedule_end_datetime__isnull=True) | models.Q(schedule_end_datetime__gte=now)
            ).count()
            return published, total
        elif section_key == 'guidelines_showcase':
            total = Guideline.objects.count()
            published = Guideline.objects.filter(is_published=True).count()
            return published, total
        elif section_key == 'headline_slider':
            total = Article.objects.filter(is_headline=True).count() + Infographic.objects.count()
            published = (
                Article.objects.filter(is_published=True, is_headline=True).count() +
                Infographic.objects.filter(is_published=True).count()
            )
            return published, total
        elif section_key == 'news_articles':
            total = Article.objects.count()
            published = Article.objects.filter(is_published=True).count()
            return published, total
        elif section_key == 'therapy_areas':
            total = TherapyArea.objects.count()
            published = TherapyArea.objects.filter(is_active=True).count()
            return published, total
        elif section_key == 'conferences':
            total = Conference.objects.count()
            published = Conference.objects.filter(is_published=True).count()
            return published, total
        elif section_key == 'education':
            total = EducationResource.objects.count()
            published = EducationResource.objects.filter(is_published=True, category__is_active=True).count()
            return published, total
        elif section_key == 'guidelines_widget':
            total = Guideline.objects.count()
            published = Guideline.objects.filter(is_published=True).count()
            return published, total
        elif section_key == 'key_highlights':
            total = KeyHighlightItem.objects.count()
            published = KeyHighlightItem.objects.filter(is_published=True).count()
            return published, total
        elif section_key == 'static_pages':
            total = Page.objects.count()
            published = Page.objects.filter(is_published=True).count()
            return published, total
    except Exception as exc:
        print(f"Error resolving counts for section {section_key}: {exc}")
    return 0, 0


class ContentSectionVisibilityCMSViewSet(viewsets.ModelViewSet):
    """
    CMS management of universal section visibility flags, live counters,
    and automatic empty-state suppression rules.
    """
    queryset = ContentSectionVisibility.objects.all()
    serializer_class = ContentSectionVisibilitySerializer
    permission_classes = [IsContentEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_enabled', 'location', 'auto_hide_if_empty']
    search_fields = ['title', 'section_key', 'description']
    ordering_fields = ['display_order', 'title', 'is_enabled']
    ordering = ['display_order', 'id']
    lookup_field = 'section_key'

    def get_queryset(self):
        ContentSectionVisibility.ensure_defaults()
        return ContentSectionVisibility.objects.all()

    def list(self, request, *args, **kwargs):
        ContentSectionVisibility.ensure_defaults()
        queryset = self.filter_queryset(self.get_queryset())
        results = []
        for sec in queryset:
            published_count, total_count = get_section_live_counts(sec.section_key)
            if not sec.is_enabled:
                public_status = 'disabled'
            elif sec.auto_hide_if_empty and published_count == 0:
                public_status = 'suppressed_empty'
            else:
                public_status = 'active'

            data = ContentSectionVisibilitySerializer(sec, context={'request': request}).data
            data['published_items_count'] = published_count
            data['total_items_count'] = total_count
            data['computed_public_status'] = public_status
            results.append(data)
        return Response(results)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        published_count, total_count = get_section_live_counts(instance.section_key)
        if not instance.is_enabled:
            public_status = 'disabled'
        elif instance.auto_hide_if_empty and published_count == 0:
            public_status = 'suppressed_empty'
        else:
            public_status = 'active'

        data = ContentSectionVisibilitySerializer(instance, context={'request': request}).data
        data['published_items_count'] = published_count
        data['total_items_count'] = total_count
        data['computed_public_status'] = public_status
        return Response(data)

    @action(detail=True, methods=['post'])
    def toggle(self, request, section_key=None):
        instance = self.get_object()
        instance.is_enabled = not instance.is_enabled
        instance.save(update_fields=['is_enabled', 'updated_at'])

        # Synchronize with SiteInfo model boolean if mapped
        site_info_field = SECTION_SITE_INFO_MAP.get(instance.section_key)
        if site_info_field:
            try:
                site_info = SiteInfo.get_solo()
                setattr(site_info, site_info_field, instance.is_enabled)
                site_info.save(update_fields=[site_info_field, 'updated_at'])
            except Exception as e:
                print(f"Failed to sync SiteInfo for {instance.section_key}: {e}")

        published_count, total_count = get_section_live_counts(instance.section_key)
        if not instance.is_enabled:
            public_status = 'disabled'
        elif instance.auto_hide_if_empty and published_count == 0:
            public_status = 'suppressed_empty'
        else:
            public_status = 'active'

        data = ContentSectionVisibilitySerializer(instance, context={'request': request}).data
        data['published_items_count'] = published_count
        data['total_items_count'] = total_count
        data['computed_public_status'] = public_status
        return Response(data)

    @action(detail=False, methods=['post'])
    def reset_defaults(self, request):
        ContentSectionVisibility.ensure_defaults()
        return self.list(request)


class ContentSectionPublicView(APIView):
    """
    Public endpoint returning visibility states and live availability for all sections.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        ContentSectionVisibility.ensure_defaults()
        sections = ContentSectionVisibility.objects.all()
        result = {}
        for sec in sections:
            published_count, total_count = get_section_live_counts(sec.section_key)
            is_visible = bool(sec.is_enabled and (not sec.auto_hide_if_empty or published_count > 0))
            result[sec.section_key] = {
                'title': sec.title,
                'location': sec.location,
                'is_enabled': sec.is_enabled,
                'auto_hide_if_empty': sec.auto_hide_if_empty,
                'published_count': published_count,
                'is_visible': is_visible,
            }
        return Response(result)



