from decimal import Decimal

from django.conf import settings
from django.db import models

from customer.models import Customer
from catalog.models import (
    PoolModel,
    HeatingOption,
    Waterfall,
    WaterTreatment,
)


class Quote(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        SENT = "sent", "Enviado"
        APPROVED = "approved", "Aprovado"
        REJECTED = "rejected", "Rejeitado"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="quotes",
    )

    pool = models.ForeignKey(
        PoolModel,
        on_delete=models.PROTECT,
    )

    heating = models.ForeignKey(
        HeatingOption,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    lighting_quantity = models.PositiveIntegerField(
        default=0,
    )

    waterfall = models.ForeignKey(
        Waterfall,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    water_treatment = models.ForeignKey(
        WaterTreatment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # Preços salvos no momento da criação do orçamento
    pool_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    heating_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    lighting_unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    waterfall_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    water_treatment_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def calculate_total(self):
        lighting_total = (
            Decimal(self.lighting_quantity) * self.lighting_unit_price
        )

        total = (
            self.pool_price
            + self.heating_price
            + lighting_total
            + self.waterfall_price
            + self.water_treatment_price
        )

        return total

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.customer}"