from django.db import models
from django.utils.text import slugify
from common.models import TimeStampedModel

class TherapyArea(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True, help_text='Therapy area or medical specialty name')
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    icon = models.CharField(
        max_length=60,
        default='Stethoscope',
        help_text='lucide-react icon component name (e.g. Heart, Stethoscope, Brain)'
    )
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0, help_text='Display ordering index')

    class Meta:
        verbose_name = 'Therapy Area'
        verbose_name_plural = 'Therapy Areas'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
