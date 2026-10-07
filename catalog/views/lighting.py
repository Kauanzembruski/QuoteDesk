from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import LightingModelForm
from catalog.models import Lighting

@login_required
def lighting_detail(request):
    lighting = Lighting.objects.first()

    return render(
        request,
        "catalog/lighting_detail.html",
        {
            "lighting": lighting,
        }
    )

@login_required
def lighting_update(request):
    lighting = Lighting.objects.first()

    if request.method == "POST":
        form = LightingModelForm(
            request.POST,
            instance=lighting
        )

        if form.is_valid():
            form.save()
            return redirect("catalog:lighting_detail")

    else:
        form = LightingModelForm(
            instance=lighting
        )

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,

            "title": "Editar Iluminação",
            "subtitle": "Atualize o valor utilizado por LED.",

            "section_title": "Informações da iluminação",
            "section_subtitle": "Defina o valor unitário e o status.",

            "back_url": "catalog:lighting_detail",
            "breadcrumb_parent": "Iluminação",

            "save_label": "Salvar Alterações",

            "item_type": "lighting",
        }
    )