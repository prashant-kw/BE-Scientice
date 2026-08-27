from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import EducationCategory, EducationResource
from .serializers import EducationCategorySerializer, EducationResourceSerializer

class EducationCategoryListView(generics.ListAPIView):
    """
    List all active high-level education categories.
    """
    serializer_class = EducationCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return EducationCategory.objects.filter(is_active=True).order_by('order', 'id')


class PatientEducationListView(generics.ListAPIView):
    """
    List patient education resources for active categories.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.PATIENT,
            category__is_active=True,
            is_published=True
        ).select_related('category').order_by('-published_at')


class MedicalEducationListView(generics.ListAPIView):
    """
    List healthcare professional / medical education resources for active categories.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.MEDICAL,
            category__is_active=True,
            is_published=True
        ).select_related('category').order_by('-published_at')


class CMEEducationListView(generics.ListAPIView):
    """
    List continuing medical education (CME) resources when CME category is active.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.CME,
            category__is_active=True,
            is_published=True
        ).select_related('category').order_by('-published_at')


class EducationResourceDetailView(generics.RetrieveAPIView):
    """
    Retrieve single education resource from an active category.
    """
    queryset = EducationResource.objects.filter(is_published=True, category__is_active=True).select_related('category')
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
