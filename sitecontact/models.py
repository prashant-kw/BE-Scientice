from django.db import models
from common.models import TimeStampedModel

class SiteInfo(TimeStampedModel):
    phone = models.CharField(max_length=60, default='+1 (800) 555-0199')
    email = models.EmailField(default='contact@scientice.org')
    address = models.TextField(default='Scientice Medical Institute, 500 Healthcare Blvd, Suite 400, Boston, MA 02115')
    facebook_url = models.URLField(blank=True, default='https://facebook.com/scientice')
    instagram_url = models.URLField(blank=True, default='https://instagram.com/scientice')
    website_url = models.URLField(blank=True, default='https://scientice.org')

    class Meta:
        verbose_name = 'Site Contact Information'
        verbose_name_plural = 'Site Contact Information'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

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
