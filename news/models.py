from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from common.models import TimeStampedModel
from therapyareas.models import TherapyArea

class Article(TimeStampedModel):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    summary = models.TextField(help_text='Short synopsis or abstract of the study/article')
    body = models.TextField(blank=True, default='', help_text='Full article content (markdown/HTML supported)')

    category = models.ForeignKey(
        TherapyArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_articles',
        help_text='Primary therapy area specialty'
    )
    category_name_override = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text='Optional compound category label (e.g. "Neurology & Endocrinology")'
    )

    image = models.ImageField(upload_to='news/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default='', help_text='External image fallback URL')

    reference_url = models.URLField(max_length=500, blank=True, default='', help_text='External reference / paper DOI URL')
    reference_name = models.CharField(max_length=200, blank=True, default='', help_text='Journal name or citation text')

    document_url = models.URLField(max_length=500, blank=True, null=True, help_text='External PDF / document link')
    document_file = models.FileField(upload_to='news_docs/', blank=True, null=True, help_text='Downloadable PDF document')

    headline_tag = models.CharField(max_length=50, default='HEADLINE', help_text='Tag badge displayed in hero (e.g. HEADLINE, BREAKTHROUGH)')
    is_headline = models.BooleanField(default=False, help_text='Display in top hero headline carousel')
    is_published = models.BooleanField(default=True, help_text='Controls whether article is publicly visible')

    read_time_minutes = models.PositiveIntegerField(default=4, help_text='Estimated read time in minutes')
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:280]
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def category_display(self):
        if self.category_name_override:
            return self.category_name_override
        if self.category:
            return self.category.name
        return 'General Medicine'

    @property
    def image_display_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    @property
    def formatted_date(self):
        return self.published_at.strftime('%d %b %Y')

    @property
    def effective_document_url(self):
        if self.document_file:
            return self.document_file.url
        return self.document_url or ''

    @property
    def formatted_read_time(self):
        return f"{self.read_time_minutes} min read"

    def __str__(self):
        return self.title
