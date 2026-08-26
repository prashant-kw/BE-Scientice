from django.db import models
from django.utils import timezone
from common.models import TimeStampedModel
from therapyareas.models import TherapyArea

class Guideline(TimeStampedModel):
    GUIDELINE_TYPE_CHOICES = [
        ('conference', 'Conference Guideline'),
        ('clinical_practice', 'Clinical Practice Guideline'),
    ]

    title = models.CharField(max_length=300)
    guideline_type = models.CharField(
        max_length=30,
        choices=GUIDELINE_TYPE_CHOICES,
        default='clinical_practice',
        help_text='Whether this is a conference congress guideline or general clinical practice guideline'
    )
    society = models.ForeignKey(
        'ConferenceSociety',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guidelines',
        help_text='Associated conference society issuer if applicable'
    )
    authority = models.CharField(max_length=150, help_text='Issuing body (e.g. ESC/EAS, ADA, ACC/AHA, KDIGO, WHO)')

    category = models.ForeignKey(
        TherapyArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guidelines',
        help_text='Primary therapy area specialty'
    )
    category_name_override = models.CharField(max_length=150, blank=True, default='')

    summary = models.TextField(blank=True, default='', help_text='Summary of recommendations')
    image = models.ImageField(upload_to='guidelines/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default='')

    document_url = models.URLField(max_length=500, blank=True, default='', help_text='External PDF / guideline link')
    document_file = models.FileField(upload_to='guidelines_docs/', blank=True, null=True)

    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Clinical Guideline'
        verbose_name_plural = 'Clinical Guidelines'
        ordering = ['-published_at']

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
        return str(self.published_at.year) if self.published_at else ''

    @property
    def effective_document_url(self):
        if self.document_file:
            return self.document_file.url
        return self.document_url or ''

    def __str__(self):
        return f"{self.title} ({self.authority})"


class ConferenceSociety(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, help_text="Acronym or short code (e.g. ESC, ACC, AHA, ADA)")
    name = models.CharField(max_length=255, help_text="Full organization name (e.g. European Society of Cardiology)")
    description = models.TextField(blank=True, default='', help_text="Brief summary or scope of society")
    website_url = models.URLField(max_length=500, blank=True, default='', help_text="Official society website URL")
    order = models.PositiveIntegerField(default=0, help_text="Display sorting order sequence")
    is_active = models.BooleanField(default=True, help_text="Whether this sub-option is displayed in website menus")

    class Meta:
        verbose_name = 'Conference Guideline Society'
        verbose_name_plural = 'Conference Guideline Societies'
        ordering = ['order', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"

