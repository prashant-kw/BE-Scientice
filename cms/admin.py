from django.contrib import admin
from .models import Page, VideoBulletin, VideoBulletinLead, VideoGenerationJob, KeyHighlightItem, ContentSectionVisibility

@admin.register(ContentSectionVisibility)
class ContentSectionVisibilityAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_key', 'location', 'is_enabled', 'auto_hide_if_empty', 'display_order', 'updated_at')
    list_filter = ('is_enabled', 'location', 'auto_hide_if_empty')
    search_fields = ('title', 'section_key', 'description')
    ordering = ('display_order', 'id')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(VideoBulletin)
class VideoBulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'avatar', 'event_title', 'show_countdown_timer', 'schedule_start_datetime', 'schedule_end_datetime', 'is_published', 'published_at', 'updated_at')
    list_filter = ('avatar', 'is_published', 'show_countdown_timer')
    search_fields = ('title', 'summary', 'script', 'event_title')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(VideoBulletinLead)
class VideoBulletinLeadAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'name', 'email', 'profession', 'bulletin', 'created_at')
    list_filter = ('profession', 'bulletin', 'created_at')
    search_fields = ('mobile', 'name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VideoGenerationJob)
class VideoGenerationJobAdmin(admin.ModelAdmin):
    list_display = ('bulletin', 'task_id', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('task_id', 'error', 'output_file', 'started_at', 'completed_at', 'created_at', 'updated_at')


@admin.register(KeyHighlightItem)
class KeyHighlightItemAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'title', 'is_published', 'order', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'summary')

