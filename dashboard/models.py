from django.conf import settings
from django.db import models


class ActivityLog(models.Model):

    class Type(models.TextChoices):
        QUOTE_CREATED = "quote_created", "Orçamento criado"
        QUOTE_UPDATED = "quote_updated", "Orçamento atualizado"
        QUOTE_DELETED = "quote_deleted", "Orçamento excluído"
        QUOTE_APPROVED = "quote_approved", "Orçamento aprovado"
        QUOTE_SENT = "quote_sent", "Orçamento enviado"

        CUSTOMER_CREATED = "customer_created", "Cliente cadastrado"
        CUSTOMER_UPDATED = "customer_updated", "Cliente atualizado"
        CUSTOMER_DELETED = "customer_deleted", "Cliente excluído"

        CATALOG_UPDATED = "catalog_updated", "Catálogo atualizado"


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )

    type = models.CharField(
        max_length=30,
        choices=Type.choices,
    )

    title = models.CharField(
        max_length=150,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return f"{self.user} - {self.title}"