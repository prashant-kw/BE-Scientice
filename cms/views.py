import csv
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, generics, permissions, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from common.permissions import IsContentEditor

from accounts.models import User
from news.models import Article
from guidelines.models import Guideline
from conferences.models import Conference, ConferenceRegistration
from education.models import EducationResource, EducationCategory
from infographics.models import Infographic
from therapyareas.models import TherapyArea
from sitecontact.models import SiteInfo, ContactMessage

from .serializers import (
    ArticleCMSSerializer,
    GuidelineCMSSerializer,
    ConferenceCMSSerializer,
    ConferenceRegistrationCMSListSerializer,
    EducationResourceCMSSerializer,
    InfographicCMSSerializer,
    TherapyAreaCMSSerializer,
    SiteInfoCMSSerializer,
    ContactMessageCMSReadSerializer,
    UserCMSListSerializer,
    PageCMSSerializer,
    PagePublicSerializer,
)

# ----------------------------------------------------------------------
# 1. Article CMS ViewSet
# ----------------------------------------------------------------------
class ArticleCMSViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().select_related('category')
    serializer_class = ArticleCMSSerializer
    permission_classes = [IsContentEditor]
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
# 4. Education Resource CMS ViewSet
# ----------------------------------------------------------------------
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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']

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
from .models import Page

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
