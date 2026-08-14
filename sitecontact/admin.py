from django.contrib import admin
from .models import SiteInfo, ContactMessage

@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'website_url', 'updated_at')

    def has_add_permission(self, request):
        # Allow creating singleton if none exists
        return not SiteInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

    def has_add_permission(self, request):
        return False
