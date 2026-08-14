from django.contrib import admin
from django.utils.html import format_html
from .models import Conference, ConferenceRegistration

class ConferenceRegistrationInline(admin.TabularInline):
    model = ConferenceRegistration
    extra = 0
    can_delete = False
    readonly_fields = ('full_name', 'email', 'attendance_mode', 'organization', 'registered_at')

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'category_display_admin',
        'start_date',
        'end_date',
        'location',
        'is_virtual_available',
        'cme_credits',
        'is_published',
    )
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('is_published', 'is_virtual_available', 'category', 'start_date')
    search_fields = ('title', 'description', 'location', 'category_name_override')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    ordering = ('start_date',)
    inlines = [ConferenceRegistrationInline]
    readonly_fields = ('created_at', 'updated_at', 'image_preview_detail')

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'category_name_override')}),
        ('Dates & Venue', {'fields': ('start_date', 'end_date', 'location', 'is_virtual_available', 'cme_credits')}),
        ('Publication Status', {'fields': ('is_published',)}),
        ('Event Details & Agenda', {'fields': ('description', 'agenda')}),
        ('Media & Image', {'fields': ('image', 'image_url', 'image_preview_detail')}),
        ('Audit Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Thumbnail')
    def image_thumbnail(self, obj):
        url = obj.image_display_url
        if url:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', url)
        return format_html('<span style="color: #999;">No image</span>')

    @admin.display(description='Image Preview')
    def image_preview_detail(self, obj):
        url = obj.image_display_url
        if url:
            return format_html('<img src="{}" style="max-width: 320px; max-height: 200px; border-radius: 8px; border: 1px solid #ddd;" />', url)
        return 'No image specified'

    @admin.display(description='Category')
    def category_display_admin(self, obj):
        return obj.category_display

@admin.register(ConferenceRegistration)
class ConferenceRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'conference', 'attendance_mode', 'organization', 'registered_at')
    list_filter = ('attendance_mode', 'conference', 'registered_at')
    search_fields = ('full_name', 'email', 'organization', 'conference__title')
    ordering = ('-registered_at',)
    readonly_fields = ('conference', 'user', 'full_name', 'email', 'attendance_mode', 'organization', 'registered_at')

    def has_add_permission(self, request):
        return False
