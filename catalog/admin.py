from django.contrib import admin

from .models import (
    PoolModel,
    HeatingOption,
    Lighting,
    Waterfall,
    WaterTreatment,
)


@admin.register(PoolModel)
class PoolModelAdmin(admin.ModelAdmin):
    list_display = (
        "model",
        "length",
        "width",
        "base_price",
        "active",
    )

    search_fields = (
        "model",
    )

    list_filter = (
        "active",
    )


@admin.register(HeatingOption)
class HeatingOptionAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "measure",
        "price",
        "active",
    )

    list_filter = (
        "type",
        "active",
    )


@admin.register(Lighting)
class LightingAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "price",
        "active",
    )

    list_filter = (
        "active",
        "type",
    )


@admin.register(Waterfall)
class WaterfallAdmin(admin.ModelAdmin):
    list_display = (
        "model",
        "price",
        "active",
    )

    search_fields = (
        "model",
    )

    list_filter = (
        "active",
    )


@admin.register(WaterTreatment)
class WaterTreatmentAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "price",
        "active",
    )

    list_filter = (
        "type",
        "active",
    )