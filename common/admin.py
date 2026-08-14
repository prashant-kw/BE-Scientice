from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'action',
        'actor_email',
        'user',
        'ip_address',
    )
    list_filter = ('action', 'timestamp')
    search_fields = ('actor_email', 'user__email', 'ip_address', 'user_agent', 'details')
    ordering = ('-timestamp',)
    readonly_fields = (
        'timestamp',
        'action',
        'actor_email',
        'user',
        'ip_address',
        'user_agent',
        'details',
    )

    def has_add_permission(self, request):
        # Insert-only via internal system events; cannot be manually created in admin UI
        return False

    def has_change_permission(self, request, obj=None):
        # Immutable audit log; modifications strictly blocked
        return False

    def has_delete_permission(self, request, obj=None):
        # Immutable audit log; deletion strictly blocked
        return False
