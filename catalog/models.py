from django.db import models

# Create your models here.
class PoolModel(models.Model):
    model = models.CharField(
        max_length=50,
    )

    length = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    width = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["model", "length", "width"],
                name="unique_pool_model_size",
            )
        ]

    def __str__(self):
        return f"{self.model} {self.length}x{self.width}"



class HeatingOption(models.Model):
    class Type(models.TextChoices):
        SOLAR = "solar", "Solar"
        HEAT_EXCHANGER = "heat_exchanger", "Trocador de calor"

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )

    measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["type", "measure"],
                name="unique_heating_type_measure",
            )
        ]

    def __str__(self):
        if self.type == self.Type.SOLAR:
            return f"{self.get_type_display()} - {self.measure} m - R$ {self.price}"
        return f"{self.get_type_display()} - {self.measure} BTU - R$ {self.price}"



class Lighting(models.Model):
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"LED - R$ {self.unit_price}"


class Waterfall(models.Model):
    model = models.CharField(
        max_length=40,
        unique=True
    )

    def __str__(self):
        return self.model

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )


class WaterTreatment(models.Model):
    class Type(models.TextChoices):
        CHLORINE = "chlorine", "Cloro"
        OZONE = "ozone", "Ozonio"

    type = models.CharField(
            max_length=20,
            choices=Type.choices,
            unique=True
        )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.get_type_display()} - R$ {self.price}"