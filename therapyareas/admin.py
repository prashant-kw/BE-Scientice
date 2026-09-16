from django.contrib import admin
from .models import TherapyArea, TherapySubArea

@admin.register(TherapyArea)
class TherapyAreaAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'slug', 'icon', 'created_at')
    list_display_links = ('name',)
    list_editable = ('order',)
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

@admin.register(TherapySubArea)
class TherapySubAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'therapy_area', 'order', 'is_active', 'created_at')
    list_display_links = ('name',)
    list_editable = ('order', 'is_active')
    list_filter = ('therapy_area', 'is_active')
    search_fields = ('name', 'therapy_area__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('therapy_area', 'order', 'name')
