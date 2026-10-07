from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=150)

    document = models.CharField(
        max_length=18,
        unique=True,
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
    )


    street = models.CharField(
        max_length=200,
    )

    number  = models.CharField(
        max_length=15,
    )

    postal_code = models.CharField(
        max_length=9,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name