from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'full_name',
        'role',
        'specialty',
        'city',
        'state',
        'is_verified',
        'is_staff',
        'date_joined',
    )
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'full_name', 'license_number', 'specialty', 'city')
    ordering = ('-date_joined',)
    list_editable = ('is_verified',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'role', 'specialty', 'license_number', 'city', 'state')}),
        ('Verification & Permissions', {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'full_name', 'role', 'specialty', 'password', 'is_verified'),
            },
        ),
    )
