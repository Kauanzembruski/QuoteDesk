from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from customer.models import Customer
from catalog.models import (
    PoolModel,
    HeatingOption,
    Lighting,
    Waterfall,
    WaterTreatment,
)


class Quote(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        SENT = "sent", "Enviado"
        APPROVED = "approved", "Aprovado"
        REJECTED = "rejected", "Rejeitado"
        CANCELLED = "cancelled", "Cancelado"


    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="quotes",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="quotes",
    )


    # Piscina
    pool = models.ForeignKey(
        PoolModel,
        on_delete=models.PROTECT,
        related_name="quotes",
    )


    # Adicionais
    heating = models.ForeignKey(
        HeatingOption,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quotes",
    )

    lighting = models.ForeignKey(
        Lighting,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quotes",
    )

    waterfall = models.ForeignKey(
        Waterfall,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quotes",
    )

    water_treatment = models.ForeignKey(
        WaterTreatment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quotes",
    )


    # Preços congelados no momento do orçamento
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

    lighting_price = models.DecimalField(
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

    validity_days = models.PositiveIntegerField(
        default=10,
        verbose_name="Validade em dias",
    )

    valid_until = models.DateField(
        null=True,
        blank=True,
    )

    commercial_notes = models.TextField(
        blank=True,
        verbose_name="Observações comerciais",
    )


    def allowed_statuses(self):
        transitions = {
            self.Status.DRAFT: (
                self.Status.SENT, self.Status.CANCELLED,
            ),
            self.Status.SENT: (
                self.Status.APPROVED, self.Status.REJECTED, self.Status.CANCELLED,
            ),
        }
        return (self.status, *transitions.get(self.status, ()))

    @property
    def is_expired(self):
        if not self.valid_until:
            return False
        if self.status not in (self.Status.DRAFT, self.Status.SENT):
            return False
        return timezone.localdate() > self.valid_until

    @property
    def is_locked(self):
        return self.status in (self.Status.CANCELLED, self.Status.REJECTED)

    def calculate_total(self):

        return (
            self.pool_price
            + self.heating_price
            + self.lighting_price
            + self.waterfall_price
            + self.water_treatment_price
        )


    def save(self, *args, **kwargs):

        self.total_price = self.calculate_total()

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Orçamento #{self.pk} - {self.customer}"
