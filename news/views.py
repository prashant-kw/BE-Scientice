from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for medical and scientific news articles.
    Supports filtering by category, therapy area, headline status, and full text search.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'body', 'category_name_override', 'reference_name']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at']

    def get_queryset(self):
        qs = Article.objects.filter(is_published=True).select_related('category')

        # Filter by therapy area / category
        therapy_param = self.request.query_params.get('therapy_area') or self.request.query_params.get('category')
        if therapy_param:
            # Clean parameter if it has suffix like " Conferences" or " Specialties"
            clean_param = therapy_param.replace(' Conferences', '').replace(' Specialties', '').strip()
            qs = qs.filter(
                Q(category__name__icontains=clean_param) |
                Q(category__slug__iexact=clean_param) |
                Q(category_name_override__icontains=clean_param)
            )

        # Filter by headline status
        headline_param = self.request.query_params.get('is_headline')
        if headline_param is not None:
            is_hl = headline_param.lower() in ['true', '1', 'yes']
            qs = qs.filter(is_headline=is_hl)

        return qs

    @action(detail=False, methods=['get'], pagination_class=None)
    def highlights(self, request):
        """
        Return headline articles for the top hero headline carousel (unpaginated).
        """
        highlights = Article.objects.filter(
            is_published=True,
            is_headline=True
        ).select_related('category').order_by('-published_at')[:8]

        serializer = self.get_serializer(highlights, many=True)
        return Response(serializer.data)
