from django.contrib import admin
from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "created_by",
        "pool",
        "status",
        "total_price",
        "created_at",
    )

    search_fields = (
        "customer__name",
        "customer__document",
        "created_by__username",
    )

    list_filter = (
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )