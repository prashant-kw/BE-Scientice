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
    event_title = models.CharField(max_length=300, blank=True, default='', help_text="Custom event title to group multiple sequential video clips (e.g. ESC Congress 2026)")
    parent_event = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_clips', help_text="Parent event bulletin if this is a secondary update video clip")
    loop_start_clip = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='loop_children', help_text="Target clip to loop back to when playlist finishes (e.g. Video #5)")
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
    avatar_position = models.CharField(max_length=20, choices=[('left', 'Left Anchor'), ('center', 'Center Anchor'), ('right', 'Right Anchor')], default='left', help_text="Presenter placement position inside newsroom background")
    avatar_scale = models.CharField(max_length=20, choices=[('standard', 'Standard (100%)'), ('medium', 'Medium (120%)'), ('large', 'Large Broadcast (140%)')], default='medium', help_text="Presenter display size scale")
    avatar_x_offset = models.FloatField(default=4.0, help_text="Presenter horizontal offset percentage (0 to 80%)")
    avatar_y_offset = models.FloatField(default=0.0, help_text="Presenter vertical offset percentage (-10 to 30%)")




    key_highlights = models.JSONField(default=list, blank=True, help_text="Structured cards array: [{number, category, title, summary, date_str, time_str}]")
    previous_events = models.JSONField(default=list, blank=True, help_text="Archive events array: [{title, location_dates, bulletins_count, video_count}]")

    video_file = models.FileField(upload_to='video_bulletins/videos/', blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, default='')
    duration_seconds = models.PositiveIntegerField(default=0)
    launch_datetime = models.DateTimeField(default=timezone.now, help_text="Scheduled launch date and time for news timer countdown on home screen.")

    # Event Countdown Timer Configuration
    show_countdown_timer = models.BooleanField(default=True, help_text="Show countdown timer below banner on homepage")
    event_start_datetime = models.DateTimeField(null=True, blank=True, help_text="Event start date and time for countdown timer")
    event_timer_label = models.CharField(max_length=200, blank=True, default='', help_text="Custom label for event countdown timer (e.g. ESC Congress 2026 Starts In)")

    # Banner Change Scheduling
    schedule_start_datetime = models.DateTimeField(null=True, blank=True, help_text="Schedule when this banner should start displaying on homepage")
    schedule_end_datetime = models.DateTimeField(null=True, blank=True, help_text="Schedule when this banner should stop displaying on homepage")

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Video News Bulletin'
        verbose_name_plural = 'Video News Bulletins'

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

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


class ContentSectionVisibility(TimeStampedModel):
    """
    Universal configuration registry tracking public visibility, live counts,
    and auto-suppression policies for all portal sections and content modules.
    """
    class SectionLocation(models.TextChoices):
        HOMEPAGE_HERO = 'homepage_hero', 'Homepage Hero & Banner'
        HOMEPAGE_GRID = 'homepage_grid', 'Homepage Dashboard Grid'
        SHOWCASE = 'showcase', 'Full-Width Showcase Section'
        NAVIGATION = 'navigation', 'Main Header Navigation'
        FOOTER = 'footer', 'Footer Area'

    section_key = models.CharField(
        max_length=60,
        unique=True,
        help_text="Unique programmatic identifier (e.g. 'news_articles', 'conferences', 'education')"
    )
    title = models.CharField(
        max_length=150,
        help_text="Human-readable title displayed in admin CMS"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Explanation of where this section appears and what content it displays"
    )
    location = models.CharField(
        max_length=30,
        choices=SectionLocation.choices,
        default=SectionLocation.HOMEPAGE_GRID,
        help_text="Visual region where this section is rendered"
    )
    icon = models.CharField(
        max_length=60,
        default='Layers',
        help_text="Lucide-react icon component name"
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text="Master toggle: If False, the section is completely hidden from public visitors"
    )
    auto_hide_if_empty = models.BooleanField(
        default=True,
        help_text="Automatically suppress section on public portal if published item count is 0"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Sorting order in CMS controls and frontend layout"
    )
    custom_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extensible parameters (e.g. max_items, custom_cta, subtitle)"
    )

    class Meta:
        verbose_name = 'Content Section Visibility'
        verbose_name_plural = 'Content Section Visibility Controls'
        ordering = ['display_order', 'id']

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.title} ({self.section_key}) - {status}"

    @classmethod
    def ensure_defaults(cls):
        """Seed or update standard platform content sections."""
        defaults = [
            {
                'section_key': 'hero_banner',
                'title': 'Top Hero Video Bulletin Banner',
                'description': 'Hero presenter video bulletin and launch countdown timer at top of homepage',
                'location': cls.SectionLocation.HOMEPAGE_HERO,
                'icon': 'Video',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 1,
            },
            {
                'section_key': 'guidelines_showcase',
                'title': 'Featured Guidelines Showcase',
                'description': 'Full-width guidelines showcase section with society tabs below hero banner',
                'location': cls.SectionLocation.SHOWCASE,
                'icon': 'BookOpen',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 2,
            },
            {
                'section_key': 'headline_slider',
                'title': 'Headline Articles & Infographics',
                'description': 'Featured breakthrough articles carousel and clinical infographic spotlight',
                'location': cls.SectionLocation.HOMEPAGE_HERO,
                'icon': 'Layers',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 3,
            },
            {
                'section_key': 'news_articles',
                'title': 'Latest News & Research Articles',
                'description': 'Medical breakthroughs and latest clinical updates column in dashboard grid',
                'location': cls.SectionLocation.HOMEPAGE_GRID,
                'icon': 'Newspaper',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 4,
            },
            {
                'section_key': 'therapy_areas',
                'title': 'Therapy Areas & Specialties Directory',
                'description': 'Medical specialties list and interactive specialties directory in grid',
                'location': cls.SectionLocation.HOMEPAGE_GRID,
                'icon': 'HeartPulse',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 5,
            },
            {
                'section_key': 'conferences',
                'title': 'Global Conferences & Symposia',
                'description': 'Upcoming medical congresses, CME accreditations, and event schedules in grid',
                'location': cls.SectionLocation.HOMEPAGE_GRID,
                'icon': 'Calendar',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 6,
            },
            {
                'section_key': 'education',
                'title': 'Awareness & Medical Education',
                'description': 'Patient education guides, medical courses, and CME presentations in grid',
                'location': cls.SectionLocation.HOMEPAGE_GRID,
                'icon': 'GraduationCap',
                'is_enabled': False,
                'auto_hide_if_empty': True,
                'display_order': 7,
            },
            {
                'section_key': 'guidelines_widget',
                'title': 'Clinical Practice Guidelines Widget',
                'description': 'Guidelines quick-access column in the main dashboard grid',
                'location': cls.SectionLocation.HOMEPAGE_GRID,
                'icon': 'BookOpen',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 8,
            },
            {
                'section_key': 'key_highlights',
                'title': 'Key Highlights Deck',
                'description': 'Global cardiology and clinical breakthrough highlights ticker',
                'location': cls.SectionLocation.HOMEPAGE_HERO,
                'icon': 'FileText',
                'is_enabled': True,
                'auto_hide_if_empty': True,
                'display_order': 9,
            },
            {
                'section_key': 'static_pages',
                'title': 'Static & Legal Pages',
                'description': 'About, Privacy Policy, Terms, and Contact institutional modal pages',
                'location': cls.SectionLocation.FOOTER,
                'icon': 'FileText',
                'is_enabled': True,
                'auto_hide_if_empty': False,
                'display_order': 10,
            },
        ]
        created_or_found = []
        for d in defaults:
            obj, _ = cls.objects.get_or_create(section_key=d['section_key'], defaults=d)
            created_or_found.append(obj)
        return created_or_found

