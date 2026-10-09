
from django import forms
from .models import (
    PoolModel,
    HeatingOption,
    Waterfall,
    Lighting,
    WaterTreatment,
)


class PoolModelForm(forms.ModelForm):
    class Meta:
        labels = {"model": "Modelo", "length": "Comprimento (m)", "width": "Largura (m)", "base_price": "Preço base (R$)", "active": "Ativo","image": "Imagem"}
        model = PoolModel

        fields = [
            "model",
            "length",
            "width",
            "base_price",
            "active",
            "image",
        ]

        widgets = {
            "image": forms.FileInput(),
        }

class HeatingModelForm(forms.ModelForm):
    class Meta:
        labels = {"type": "Tipo", "measure": "Medida", "price": "Preço (R$)", "active": "Ativo"}
        help_texts = {"measure": "Informe em metros para solar ou BTU para trocador de calor."}
        model = HeatingOption

        fields = [
            "type",
            "measure",
            "price",
            "active",
        ]

class WaterfallModelForm(forms.ModelForm):
    class Meta:
        model = Waterfall
        error_messages = {"model": {"unique": "Este modelo já está cadastrado."}}

        fields = [
            "model",
            "price",
            "active",
        ]

        labels = {
            "model": "Modelo",
            "price": "Preço (R$)",
            "active": "Ativo",
        }

class LightingModelForm(forms.ModelForm):
    class Meta:
        model = Lighting
        error_messages = {"type": {"unique": "Este tipo já está cadastrado."}}

        fields = [
            "type",
            "price",
            "active",
        ]

        labels = {
            "type": "Kit",
            "price": "Preço",
            "active": "Ativo",
        }


class LightingPriceForm(forms.ModelForm):
    class Meta:
        model = Lighting
        fields = ["price"]
        error_messages = {"price": {
            "required": "Informe o preço.",
            "invalid": "Informe um preço válido.",
            "max_digits": "O preço informado excede o limite permitido.",
            "max_decimal_places": "Informe o preço com no máximo duas casas decimais.",
        }}


class TreatmentPriceForm(LightingPriceForm):
    class Meta(LightingPriceForm.Meta):
        model = WaterTreatment
