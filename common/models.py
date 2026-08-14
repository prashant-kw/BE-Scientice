from django.db import models
from django.conf import settings

class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AuditLog(models.Model):
    """
    Immutable security audit trail strictly scoped to authentication lifecycle events:
    - LOGIN_SUCCESS: Successful user/admin authentication
    - LOGIN_FAILED: Failed login attempt (with targeted email & IP)
    - USER_REGISTERED: New user account creation
    - LOGOUT: Session termination & token blacklist

    NOTE: Content CRUD events (add/change/delete on articles, guidelines, conferences, etc.)
    are recorded automatically by Django's native `django.contrib.admin.models.LogEntry`.
    Do not duplicate CMS content logging here.
    """
    class Action(models.TextChoices):
        LOGIN_SUCCESS = 'LOGIN_SUCCESS', 'Login Success'
        LOGIN_FAILED = 'LOGIN_FAILED', 'Login Failed'
        USER_REGISTERED = 'USER_REGISTERED', 'User Registered'
        LOGOUT = 'LOGOUT', 'Logout'
        PASSWORD_CHANGED = 'PASSWORD_CHANGED', 'Password Changed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auth_audit_logs',
        help_text='Associated user account if resolved'
    )
    actor_email = models.EmailField(
        'attempted / authenticated email',
        blank=True,
        default='',
        help_text='Email address used during the auth event'
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        db_index=True
    )
    ip_address = models.GenericIPAddressField(
        'IP Address',
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        'User Agent',
        blank=True,
        default=''
    )
    details = models.JSONField(
        'Context Details',
        default=dict,
        blank=True
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Authentication Audit Log'
        verbose_name_plural = 'Authentication Audit Logs'

    def __str__(self):
        email_repr = self.actor_email or (self.user.email if self.user else 'Anonymous')
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.action} ({email_repr}) - IP: {self.ip_address or 'Unknown'}"
