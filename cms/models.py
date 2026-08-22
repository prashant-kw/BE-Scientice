from django.db import models
from django.utils import timezone
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


class VideoBulletin(TimeStampedModel):
    """CMS-managed presenter-style video news report."""

    class Avatar(models.TextChoices):
        FEMALE_DOCTOR = 'female_doctor', 'Female Doctor'
        MALE_DOCTOR = 'male_doctor', 'Male Doctor'
        FEMALE_ANCHOR = 'female_anchor', 'Female News Anchor'
        MALE_ANCHOR = 'male_anchor', 'Male News Anchor'
        CUSTOM = 'custom', 'Custom Avatar'

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True)
    eyebrow = models.CharField(max_length=120, blank=True, default='GLOBAL CARDIOLOGY BULLETIN')
    summary = models.TextField(blank=True, default='')
    script = models.TextField(help_text='Narration spoken by the selected avatar')
    bullet_points = models.JSONField(default=list, blank=True)

    background_image = models.ImageField(upload_to='video_bulletins/backgrounds/', blank=True, null=True)
    background_image_url = models.URLField(max_length=500, blank=True, default='')
    promo_banner_image = models.ImageField(upload_to='video_bulletins/banners/', blank=True, null=True, help_text="Optional banner image specifically for homepage news promo card")
    avatar = models.CharField(max_length=30, choices=Avatar.choices, default=Avatar.FEMALE_DOCTOR)
    voice_gender = models.CharField(max_length=10, choices=[('female', 'Female Voice'), ('male', 'Male Voice')], default='female')
    custom_avatar_image = models.ImageField(upload_to='video_bulletins/avatars/', blank=True, null=True)


    key_highlights = models.JSONField(default=list, blank=True, help_text="Structured cards array: [{number, category, title, summary, date_str, time_str}]")
    previous_events = models.JSONField(default=list, blank=True, help_text="Archive events array: [{title, location_dates, bulletins_count, video_count}]")

    video_file = models.FileField(upload_to='video_bulletins/videos/', blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, default='')
    duration_seconds = models.PositiveIntegerField(default=0)
    launch_datetime = models.DateTimeField(default=timezone.now, help_text="Scheduled launch date and time for news timer countdown on home screen.")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Video News Bulletin'
        verbose_name_plural = 'Video News Bulletins'

    def __str__(self):
        return self.title


class KeyHighlightItem(TimeStampedModel):
    """Standalone global news highlight card managed independently in CMS."""
    number = models.CharField(max_length=10, default='01')
    category = models.CharField(max_length=100, default='HEART FAILURE')
    title = models.CharField(max_length=300)
    summary = models.TextField(blank=True, default='')
    date_str = models.CharField(max_length=50, default='12 Aug 2026')
    time_str = models.CharField(max_length=50, default='09:15')
    article_link = models.CharField(max_length=500, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Key Highlight Item'
        verbose_name_plural = 'Key Highlight Items'

    def __str__(self):
        return f'{self.number} - {self.title}'



class VideoBulletinLead(TimeStampedModel):
    bulletin = models.ForeignKey(VideoBulletin, on_delete=models.CASCADE, related_name='leads')
    mobile = models.CharField(max_length=30)
    name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    hospital_name = models.CharField(max_length=255, blank=True, default='')
    profession = models.CharField(max_length=100, blank=True, default='')

    interests = models.JSONField(default=list, blank=True)
    consent = models.BooleanField(default=True)


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video Bulletin Subscriber'
        verbose_name_plural = 'Video Bulletin Subscribers'

    def __str__(self):
        return f'{self.mobile} - {self.bulletin.title}'


class VideoGenerationJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        AUDIO = 'audio', 'Generating narration'
        AVATAR = 'avatar', 'Animating presenter'
        COMPOSING = 'composing', 'Composing newsroom video'
        READY = 'ready', 'Ready for review'
        FAILED = 'failed', 'Failed'

    bulletin = models.ForeignKey(VideoBulletin, on_delete=models.CASCADE, related_name='generation_jobs')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    progress = models.PositiveSmallIntegerField(default=0)
    task_id = models.CharField(max_length=255, blank=True, default='')
    error = models.TextField(blank=True, default='')
    output_file = models.FileField(upload_to='video_bulletins/generated/', blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.bulletin.title}: {self.get_status_display()}'
