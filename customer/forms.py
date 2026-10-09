import re

from django import forms
from django.db.models import Value
from django.db.models.functions import Replace, Trim

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer

        fields = [
            "name",
            "document",
            "phone",
            "email",
            "city",
            "street",
            "number",
            "postal_code",
        ]

        error_messages = {
            "document": {"unique": "Este CPF/CNPJ já está cadastrado."},
            "email": {"invalid": "Informe um e-mail válido."},
            "name": {"required": "Informe o nome do cliente.", "unique": "Este nome já está cadastrado."},
        }

    def clean_document(self):
        document = self.cleaned_data.get("document")
        if not document:
            return None
        if not re.fullmatch(r"[0-9. /-]+", document):
            raise forms.ValidationError("Informe um CPF com 11 dígitos ou CNPJ com 14 dígitos.")
        digits = re.sub(r"[^0-9]", "", document)
        if len(digits) not in (11, 14):
            raise forms.ValidationError("Informe um CPF com 11 dígitos ou CNPJ com 14 dígitos.")
        normalized = Trim("document")
        for separator in (".", "-", "/", " "):
            normalized = Replace(normalized, Value(separator), Value(""))
        duplicates = Customer.objects.annotate(document_digits=normalized).filter(document_digits=digits)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("Este CPF/CNPJ já está cadastrado.")
        return digits

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not re.fullmatch(r"[0-9 ()+-]+", phone):
            raise forms.ValidationError("Informe um telefone com DDD e 10 ou 11 dígitos.")
        digits = re.sub(r"[^0-9]", "", phone)
        if digits.startswith("55") and len(digits) in (12, 13):
            digits = digits[2:]
        if len(digits) not in (10, 11):
            raise forms.ValidationError("Informe um telefone com DDD e 10 ou 11 dígitos.")
        return digits

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if not postal_code:
            return None
        if not re.fullmatch(r"[0-9]{5}-?[0-9]{3}", postal_code):
            raise forms.ValidationError("Informe um CEP com 8 dígitos.")
        return postal_code.replace("-", "")
