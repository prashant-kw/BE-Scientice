from django.contrib import admin
from django.utils.html import format_html
from .models import Guideline

@admin.register(Guideline)
class GuidelineAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'authority',
        'category_display_admin',
        'formatted_date',
        'is_published',
    )
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('authority', 'category', 'is_published', 'published_at')
    search_fields = ('title', 'authority', 'summary', 'category_name_override')
    list_editable = ('is_published',)
    ordering = ('-published_at',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview_detail')

    fieldsets = (
        (None, {'fields': ('title', 'authority', 'category', 'category_name_override')}),
        ('Publication Details', {'fields': ('is_published', 'published_at')}),
        ('Summary & Protocol', {'fields': ('summary',)}),
        ('Media & Documents', {'fields': ('image', 'image_url', 'image_preview_detail', 'document_url', 'document_file')}),
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
