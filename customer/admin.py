from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "document",
        "phone",
        "city",
        "created_at",
    )

    search_fields = (
        "name",
        "document",
        "phone",
        "email",
    )

    list_filter = (
        "city",
        "created_at",
    )