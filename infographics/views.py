from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Infographic
from .serializers import InfographicSerializer

class InfographicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing clinical infographics and visual summaries.
    """
    serializer_class = InfographicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'subtitle', 'category', 'quote', 'alert']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']
    pagination_class = None  # Infographics are displayed in hero tabs / carousel

    def get_queryset(self):
        return Infographic.objects.filter(is_published=True).prefetch_related('points')
