from django.contrib import admin
from .models import TherapyArea

@admin.register(TherapyArea)
class TherapyAreaAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'slug', 'icon', 'created_at')
    list_display_links = ('name',)
    list_editable = ('order',)
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
