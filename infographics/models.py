from django.db import models
from django.utils import timezone
from common.models import TimeStampedModel

class Infographic(TimeStampedModel):
    title = models.CharField(max_length=300)
    tag = models.CharField(max_length=60, default='INFOGRAPHIC', help_text='Display badge/tag (e.g. INFOGRAPHIC, CLINICAL PATHWAY)')
    subtitle = models.TextField(blank=True, default='')
    category = models.CharField(max_length=150, blank=True, default='Clinical Guidelines')

    image = models.ImageField(upload_to='infographics/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default='', help_text='External infographic image URL')

    reference = models.CharField(max_length=300, blank=True, default='')
    reference_url = models.URLField(max_length=500, blank=True, default='')

    document_url = models.URLField(max_length=500, blank=True, null=True, help_text='External PDF / document link')
    document_file = models.FileField(upload_to='infographics_docs/', blank=True, null=True, help_text='Downloadable PDF version')

    quote = models.TextField(blank=True, default='', help_text='Key highlight quote')
    alert = models.TextField(blank=True, default='', help_text='Critical clinical alert or warning box')

    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Infographic'
        verbose_name_plural = 'Infographics'
        ordering = ['-published_at', '-created_at']

    @property
    def image_display_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    @property
    def effective_document_url(self):
        if self.document_file:
            return self.document_file.url
        return self.document_url or ''

    def __str__(self):
        return self.title

class InfographicPoint(models.Model):
    infographic = models.ForeignKey(Infographic, on_delete=models.CASCADE, related_name='points')
    order = models.PositiveIntegerField(default=1, help_text='Step/point index (e.g. 1, 2, 3)')
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        verbose_name = 'Infographic Key Point'
        verbose_name_plural = 'Infographic Key Points'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.order}. {self.title}"
