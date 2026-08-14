from django.db import models
from common.models import TimeStampedModel

class Page(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier (e.g. 'privacy-policy')")
    content = models.TextField(blank=True, default='', help_text="Rich text content of the page")
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Static Page'
        verbose_name_plural = 'Static Pages'
        ordering = ['title']

    def __str__(self):
        return self.title
