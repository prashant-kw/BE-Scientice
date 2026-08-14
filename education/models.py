from django.db import models
from django.utils import timezone
from common.models import TimeStampedModel

class EducationCategory(TimeStampedModel):
    class Key(models.TextChoices):
        PATIENT = 'patient', 'Patient Education'
        MEDICAL = 'medical', 'Medical Education'
        CME = 'cme', 'CME & Guidelines'

    key = models.CharField(max_length=30, choices=Key.choices, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=60, default='BookOpen', help_text='lucide-react icon name (e.g. Users, GraduationCap, FileCheck)')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Education Category'
        verbose_name_plural = 'Education Categories'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.key})"

class EducationResource(TimeStampedModel):
    category = models.ForeignKey(EducationCategory, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='', help_text='Brief summary or resource overview')
    body = models.TextField(blank=True, default='', help_text='Full markdown or HTML content')
    icon = models.CharField(max_length=60, blank=True, default='')

    file = models.FileField(upload_to='education_docs/', blank=True, null=True, help_text='Downloadable PDF or presentation')
    external_url = models.URLField(max_length=500, blank=True, default='', help_text='Link to external course or webinar')

    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Education Resource'
        verbose_name_plural = 'Education Resources'
        ordering = ['-published_at']

    @property
    def file_url(self):
        return self.file.url if self.file else ''

    def __str__(self):
        return f"{self.title} [{self.category.get_key_display()}]"
