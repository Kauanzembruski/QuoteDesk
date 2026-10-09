from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


NON_NEGATIVE = MinValueValidator(0, message="O valor não pode ser negativo.")
POSITIVE_MEASURE = MinValueValidator(Decimal("0.01"), message="A medida deve ser maior que zero.")

# Create your models here.
class PoolModel(models.Model):
    model = models.CharField(
        max_length=50
    )

    length = models.DecimalField(
        validators=[POSITIVE_MEASURE],
        max_digits=5,
        decimal_places=2
    )

    width = models.DecimalField(
        validators=[POSITIVE_MEASURE],
        max_digits=5,
        decimal_places=2
    )

    base_price = models.DecimalField(
        validators=[NON_NEGATIVE],
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="pools/",
        null=True,
        blank=True,
    )

    active = models.BooleanField(
        default=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(base_price__gte=0), name="pool_price_non_negative"),
            models.CheckConstraint(condition=models.Q(length__gt=0, width__gt=0), name="pool_dimensions_positive"),
            models.UniqueConstraint(
                fields=["model", "length", "width"],
                name="unique_pool_model_size",
                violation_error_message="Já existe uma piscina com este modelo e estas medidas.",
            )
        ]

    def __str__(self):
        return self.model



class HeatingOption(models.Model):
    class Type(models.TextChoices):
        SOLAR = "solar", "Solar"
        HEAT_EXCHANGER = "heat_exchanger", "Trocador de calor"

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
    )

    measure = models.DecimalField(
        validators=[POSITIVE_MEASURE],
        max_digits=10,
        decimal_places=2,
    )

    price = models.DecimalField(
        validators=[NON_NEGATIVE],
        max_digits=10,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="heating_price_non_negative"),
            models.CheckConstraint(condition=models.Q(measure__gt=0), name="heating_measure_positive"),
            models.UniqueConstraint(
                fields=["type", "measure"],
                name="unique_heating_type_measure",
                violation_error_message="Já existe um aquecimento com este tipo e esta medida.",
            )
        ]

    @property
    def measure_unit(self):
        return "m" if self.type == self.Type.SOLAR else "BTU"

    def __str__(self):
        if self.type == self.Type.SOLAR:
            return f"{self.get_type_display()} - {self.measure} m - R$ {self.price}"
        return f"{self.get_type_display()} - {self.measure} BTU - R$ {self.price}"



class Lighting(models.Model):

    class Type(models.TextChoices):
        KIT_2 = "kit_2", "Kit 2 LEDs"
        KIT_4 = "kit_4", "Kit 4 LEDs"

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        unique=True,
    )

    price = models.DecimalField(
        validators=[NON_NEGATIVE],
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.get_type_display()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="lighting_price_non_negative"),
        ]


class Waterfall(models.Model):
    model = models.CharField(
        max_length=40,
        unique=True
    )

    def __str__(self):
        return self.model

    price = models.DecimalField(
        validators=[NON_NEGATIVE],
        max_digits=10,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="waterfall_price_non_negative"),
        ]


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
        validators=[NON_NEGATIVE],
        max_digits=10,
        decimal_places=2,
    )
    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.get_type_display()} - R$ {self.price}"

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="treatment_price_non_negative"),
        ]
