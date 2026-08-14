from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Guideline
from .serializers import GuidelineSerializer

class GuidelineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing clinical practice guidelines.
    Supports filtering by therapy area and search by title or issuing authority.
    """
    serializer_class = GuidelineSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'authority', 'summary', 'category_name_override']
    ordering_fields = ['published_at', 'title', 'authority']
    ordering = ['-published_at']

    def get_queryset(self):
        qs = Guideline.objects.filter(is_published=True).select_related('category')

        therapy_param = self.request.query_params.get('therapy_area') or self.request.query_params.get('category')
        if therapy_param:
            clean_param = therapy_param.replace(' Conferences', '').replace(' Specialties', '').strip()
            qs = qs.filter(
                Q(category__name__icontains=clean_param) |
                Q(category__slug__iexact=clean_param) |
                Q(category_name_override__icontains=clean_param)
            )

        return qs
