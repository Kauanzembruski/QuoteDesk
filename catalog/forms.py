
from django import forms
from .models import (
    PoolModel,
    HeatingOption,
    Waterfall,
    Lighting
)


class PoolModelForm(forms.ModelForm):
    class Meta:
        labels = {"model": "Modelo", "length": "Comprimento (m)", "width": "Largura (m)", "base_price": "Pre?o base (R$)", "active": "Ativo","image": "Imagem"}
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
        labels = {"type": "Tipo", "measure": "Medida", "price": "Pre?o (R$)", "active": "Ativo"}
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