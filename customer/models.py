from django.db import models


class Customer(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
    )

    document = models.CharField(
        max_length=18,
        unique=True,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=15,
    )

    email = models.EmailField(
        blank=True,
        max_length=50,
    )

    city = models.CharField(
        max_length=100,
    ) 

    neighborhood = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )


    street = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    number  = models.CharField(
        max_length=15,
        null=True,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=9,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name