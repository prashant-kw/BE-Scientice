from django.db import models
from common.models import TimeStampedModel

class SiteInfo(TimeStampedModel):
    phone = models.CharField(max_length=60, blank=True, null=True, default='+1 (800) 555-0199')
    email = models.EmailField(blank=True, null=True, default='contact@scientice.org')
    address = models.TextField(blank=True, null=True, default='Scientice Medical Institute, 500 Healthcare Blvd, Suite 400, Boston, MA 02115')
    facebook_url = models.URLField(blank=True, null=True, default='https://facebook.com/scientice')
    instagram_url = models.URLField(blank=True, null=True, default='https://instagram.com/scientice')
    website_url = models.URLField(blank=True, null=True, default='https://scientice.org')

    # Portal Homepage Section Visibility Controls
    show_hero_banner = models.BooleanField(default=True, help_text='Show Top Event Hero Promo Banner on Homepage')
    show_guidelines_showcase = models.BooleanField(default=True, help_text='Show Featured Guidelines Showcase Section below Hero Banner')
    show_headline_slider = models.BooleanField(default=True, help_text='Show Headline Articles Slider & Infographics')
    show_news_widget = models.BooleanField(default=True, help_text='Show Latest News widget in dashboard grid')
    show_therapy_areas_widget = models.BooleanField(default=True, help_text='Show Therapy Areas widget in dashboard grid')
    show_conferences_widget = models.BooleanField(default=True, help_text='Show Conferences widget in dashboard grid')
    show_education_widget = models.BooleanField(default=False, help_text='Show Education widget in dashboard grid')
    show_guidelines_widget = models.BooleanField(default=True, help_text='Show Guidelines widget in dashboard grid')


    class Meta:
        verbose_name = 'Site Contact Information'
        verbose_name_plural = 'Site Contact Information'

    @classmethod
    def get_solo(cls):
        try:
            obj, _ = cls.objects.get_or_create(pk=1)
            return obj
        except Exception:
            try:
                return cls.objects.filter(pk=1).first() or cls(pk=1)
            except Exception:
                return cls(pk=1)

    def __str__(self):
        return f"Scientice Site Contact Info ({self.email})"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True, default='General Inquiry')
    message = models.TextField()
    is_read = models.BooleanField(default=False, help_text='Mark message as read/reviewed by editorial staff')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Inbound Contact Message'
        verbose_name_plural = 'Inbound Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.subject} ({self.created_at.strftime('%d %b %Y')})"
