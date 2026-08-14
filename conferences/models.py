from django.db import models
from django.utils.text import slugify
from common.models import TimeStampedModel
from therapyareas.models import TherapyArea
from accounts.models import User

class Conference(TimeStampedModel):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    agenda = models.JSONField(default=list, blank=True, help_text='List of agenda topics or tracks as strings')

    category = models.ForeignKey(
        TherapyArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conferences',
        help_text='Primary therapy area specialty'
    )
    category_name_override = models.CharField(max_length=150, blank=True, default='')

    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200, help_text='e.g. Paris, France or Boston, MA & Virtual')
    is_virtual_available = models.BooleanField(default=True, help_text='Whether online attendance is supported')
    cme_credits = models.PositiveIntegerField(null=True, blank=True, help_text='CME / CPD credit hours')

    image = models.ImageField(upload_to='conferences/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default='')

    document_url = models.URLField(max_length=500, blank=True, null=True, help_text='External PDF / document link')
    document_file = models.FileField(upload_to='conferences_docs/', blank=True, null=True, help_text='Downloadable agenda or brochure PDF')

    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Conference'
        verbose_name_plural = 'Conferences'
        ordering = ['start_date', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:280]
            slug = base_slug
            counter = 1
            while Conference.objects.filter(slug=slug).exclude(pk=self.pk).exists():
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
        return 'Medical Science'

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

    @property
    def formatted_date(self):
        if not self.start_date:
            return ''
        if not self.end_date or self.start_date == self.end_date:
            return self.start_date.strftime('%d %b %Y')

        # If same month and year
        if self.start_date.year == self.end_date.year and self.start_date.month == self.end_date.month:
            return f"{self.start_date.day}-{self.end_date.day} {self.start_date.strftime('%b %Y')}"
        # If same year but different month
        if self.start_date.year == self.end_date.year:
            return f"{self.start_date.strftime('%d %b')} - {self.end_date.strftime('%d %b %Y')}"
        return f"{self.start_date.strftime('%d %b %Y')} - {self.end_date.strftime('%d %b %Y')}"

    def __str__(self):
        return f"{self.title} ({self.formatted_date})"

class ConferenceRegistration(models.Model):
    class Mode(models.TextChoices):
        IN_PERSON = 'in_person', 'In-Person Attendance'
        VIRTUAL = 'virtual', 'Virtual / Online Attendance'

    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='conference_registrations')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    attendance_mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.VIRTUAL)
    organization = models.CharField(max_length=255, blank=True, default='')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conference Registration'
        verbose_name_plural = 'Conference Registrations'
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.full_name} - {self.conference.title} ({self.get_attendance_mode_display()})"
