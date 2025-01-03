"""Django admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdminPages(BaseUserAdmin):
    """Define the admin pages for users
    """
    ordering = ['id']
    list_display = ['email', 'name']
    # Defines the fields for editing the model in the admin site
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'), # section title
            {
                'fields': ( # section fields
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']

    # Customize the adding data to model page in admin site
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # for styling and formatting of page
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdminPages)