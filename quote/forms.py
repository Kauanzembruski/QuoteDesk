from django import forms

from .models import Quote
from catalog.models import (
    PoolModel,
    HeatingOption,
    Lighting,
    Waterfall,
    WaterTreatment,
)


class QuoteModelForm(forms.ModelForm):
    class Meta:
        model = Quote

        fields = [
            "customer",
            "pool",
            "heating",
            "lighting",
            "waterfall",
            "water_treatment",
            "status",
        ]

        labels = {
            "customer": "Cliente",
            "pool": "Piscina",
            "heating": "Aquecimento",
            "lighting": "Iluminação",
            "waterfall": "Cascata",
            "water_treatment": "Tratamento da água",
            "status": "Status",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["pool"].queryset = PoolModel.objects.filter(
            active=True
        )

        self.fields["heating"].queryset = HeatingOption.objects.filter(
            active=True
        )

        self.fields["lighting"].queryset = Lighting.objects.filter(
            active=True
        )

        self.fields["waterfall"].queryset = Waterfall.objects.filter(
            active=True
        )

        self.fields["water_treatment"].queryset = WaterTreatment.objects.filter(
            active=True
        )

        self.fields["customer"].empty_label = "Selecione um cliente"
        self.fields["pool"].empty_label = "Selecione uma piscina"

        self.fields["heating"].empty_label = "Sem aquecimento"
        self.fields["lighting"].empty_label = "Sem iluminação"
        self.fields["waterfall"].empty_label = "Sem cascata"
        self.fields["water_treatment"].empty_label = "Sem tratamento"