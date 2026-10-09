from django import forms
from django.core.exceptions import ValidationError

from .models import Quote
from catalog.models import (
    PoolModel,
    HeatingOption,
    Lighting,
    Waterfall,
    WaterTreatment,
)


class ActiveCatalogChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        try:
            return super().to_python(value)
        except (ValidationError, ValueError, TypeError, OverflowError):
            try:
                inactive = self.queryset.model.objects.filter(pk=value, active=False).exists()
            except (ValueError, TypeError, OverflowError):
                inactive = False
            if inactive:
                raise ValidationError("Este item está inativo e não pode ser selecionado.")
            raise ValidationError("Selecione um item válido.")


class QuoteModelForm(forms.ModelForm):
    class Meta:
        model = Quote
        field_classes = {
            field: ActiveCatalogChoiceField
            for field in ("pool", "heating", "lighting", "waterfall", "water_treatment")
        }

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
        self.originally_locked = bool(self.instance.pk and self.instance.is_locked)
        allowed = (
            self.instance.allowed_statuses()
            if self.instance.pk else (Quote.Status.DRAFT,)
        )
        self.fields["status"].choices = [
            choice for choice in Quote.Status.choices if choice[0] in allowed
        ]
        self.fields["status"].error_messages["invalid_choice"] = (
            "Esta alteração de status não é permitida."
        )

        self.fields["pool"].queryset = PoolModel.objects.filter(
            active=True
        )

        self.fields["heating"].queryset = HeatingOption.objects.filter(
            active=True, type__in=HeatingOption.Type.values,
        )

        self.fields["lighting"].queryset = Lighting.objects.filter(
            active=True, type__in=Lighting.Type.values,
        )

        self.fields["waterfall"].queryset = Waterfall.objects.filter(
            active=True
        )

        self.fields["water_treatment"].queryset = WaterTreatment.objects.filter(
            active=True, type__in=WaterTreatment.Type.values,
        )

        self.fields["customer"].empty_label = "Selecione um cliente"
        self.fields["pool"].empty_label = "Selecione uma piscina"

        self.fields["heating"].empty_label = "Sem aquecimento"
        self.fields["lighting"].empty_label = "Sem iluminação"
        self.fields["waterfall"].empty_label = "Sem cascata"
        self.fields["water_treatment"].empty_label = "Sem tratamento"

    def clean_status(self):
        status = self.cleaned_data["status"]
        # Validate on the server even when the HTML choices are bypassed.
        if self.instance.pk:
            allowed = self.instance.allowed_statuses()
        else:
            allowed = (Quote.Status.DRAFT,)
        if status not in allowed:
            raise forms.ValidationError("Esta alteração de status não é permitida.")
        return status

    def clean(self):
        cleaned_data = super().clean()
        if self.originally_locked:
            raise forms.ValidationError(
                "Orçamentos cancelados ou rejeitados não podem ser alterados."
            )
        if not self.errors and cleaned_data.get("pool"):
            total = cleaned_data["pool"].base_price
            for field in ("heating", "lighting", "waterfall", "water_treatment"):
                item = cleaned_data.get(field)
                if item:
                    total += item.price
            try:
                Quote._meta.get_field("total_price").clean(total, self.instance)
            except ValidationError:
                raise forms.ValidationError("O total do orçamento excede o limite permitido.")
        return cleaned_data


class QuoteUpdateForm(QuoteModelForm):
    class Meta(QuoteModelForm.Meta):
        fields = QuoteModelForm.Meta.fields + [
            "validity_days",
            "commercial_notes",
        ]

        labels = {
            **QuoteModelForm.Meta.labels,
            "validity_days": "Validade em dias",
            "commercial_notes": "Observações comerciais",
        }

        widgets = {
            "validity_days": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 365,
                }
            ),

            "commercial_notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ex.: instalação não inclusa, condição de pagamento, prazo combinado...",
                }
            ),
        }