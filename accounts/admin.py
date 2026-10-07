from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "QuoteDesk",
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
            "QuoteDesk",
            {
                "fields": (
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
        "email",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )