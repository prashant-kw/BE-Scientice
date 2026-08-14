from django.contrib import admin
from django.utils.html import format_html
from .models import Infographic, InfographicPoint

class InfographicPointInline(admin.TabularInline):
    model = InfographicPoint
    extra = 1
    fields = ('order', 'title', 'description')
    ordering = ('order',)

@admin.register(Infographic)
class InfographicAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'title', 'tag', 'category', 'is_published', 'published_at')
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('tag', 'category', 'is_published', 'published_at')
    search_fields = ('title', 'subtitle', 'quote', 'alert', 'category')
    list_editable = ('is_published',)
    ordering = ('-published_at',)
    inlines = [InfographicPointInline]
    readonly_fields = ('created_at', 'updated_at', 'image_preview_detail')

    fieldsets = (
        (None, {'fields': ('title', 'tag', 'category', 'subtitle')}),
        ('Publication Status', {'fields': ('is_published', 'published_at')}),
        ('Highlights & Alerts', {'fields': ('quote', 'alert')}),
        ('Media & Image', {'fields': ('image', 'image_url', 'image_preview_detail')}),
        ('References', {'fields': ('reference', 'reference_url')}),
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
