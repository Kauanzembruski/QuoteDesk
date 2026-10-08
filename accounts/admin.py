from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informações adicionais",
            {
                "fields": (
                    "phone",
                    "photo",
                    "role",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informações adicionais",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "photo",
                    "role",
                )
            },
        ),
    )

    list_display = (
        "username",
        "first_name",
        "last_name",
        "role",
        "is_active",
    )