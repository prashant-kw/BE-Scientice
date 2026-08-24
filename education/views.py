from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import EducationCategory, EducationResource
from .serializers import EducationCategorySerializer, EducationResourceSerializer

class EducationCategoryListView(generics.ListAPIView):
    """
    List all high-level education categories that have active published resources.
    """
    serializer_class = EducationCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return EducationCategory.objects.filter(
            resources__is_published=True
        ).distinct().order_by('order', 'id')


class PatientEducationListView(generics.ListAPIView):
    """
    List patient education resources.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.PATIENT,
            is_published=True
        ).select_related('category').order_by('-published_at')

class MedicalEducationListView(generics.ListAPIView):
    """
    List healthcare professional / medical education resources.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.MEDICAL,
            is_published=True
        ).select_related('category').order_by('-published_at')

class CMEEducationListView(generics.ListAPIView):
    """
    List continuing medical education (CME) resources and courseware.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.CME,
            is_published=True
        ).select_related('category').order_by('-published_at')

class EducationResourceDetailView(generics.RetrieveAPIView):
    """
    Retrieve single education resource.
    """
    queryset = EducationResource.objects.filter(is_published=True).select_related('category')
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
