from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        SELLER = "seller", "Vendedor"

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    photo = models.ImageField(
        upload_to="users/",
        blank=True,
        null=True,
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.SELLER,
    )

    def __str__(self):
        return self.get_full_name() or self.username