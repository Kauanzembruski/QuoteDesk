from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import HeatingModelForm
from catalog.models import HeatingOption


@login_required
def heating_list(request):
    heating_options = HeatingOption.objects.all()

    return render(
        request,
        "catalog/heating_list.html",
        {
            "heating_options": heating_options,
            "title": "Aquecimento",
            "subtitle": "Gerencie as opções de aquecimento cadastradas no catálogo.",
            "create_url": "catalog:heating_create",
            "create_label": "Novo Aquecimento",
            "search_placeholder": "Buscar por tipo ou medida...",
        }
    )


@login_required
def heating_create(request):
    if request.method == "POST":
        form = HeatingModelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("catalog:heating_list")

    else:
        form = HeatingModelForm()

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,

            "title": "Novo Aquecimento",
            "subtitle": "Cadastre uma nova opção de aquecimento no catálogo.",

            "section_title": "Informações do aquecimento",
            "section_subtitle": "Informe o tipo, medida e valor.",

            "back_url": "catalog:heating_list",
            "breadcrumb_parent": "Aquecimento",

            "save_label": "Salvar Aquecimento",

            "item_type": "heating",
        }
    )


@login_required
def heating_detail(request, pk):
    heating = get_object_or_404(
        HeatingOption,
        pk=pk
    )

    return render(
        request,
        "catalog/heating_detail.html",
        {
            "heating": heating,
            "item": heating,
            "item_name": heating.get_type_display(),
            "item_summary": f"{heating.measure} {heating.measure_unit}",
            "item_price": heating.price,
            "price_label": "Pre?o",
            "breadcrumb_parent": "Aquecimento",
            "section_title": "Informa??es do aquecimento",
            "subtitle": "Informa??es do item cadastrado no cat?logo.",
            "back_url": reverse("catalog:heating_list"),
            "update_url": reverse("catalog:heating_update", kwargs={"pk": heating.pk}),
            "delete_url": reverse("catalog:heating_delete", kwargs={"pk": heating.pk}),
        }
    )


@login_required
def heating_update(request, pk):
    heating = get_object_or_404(
        HeatingOption,
        pk=pk
    )

    if request.method == "POST":
        form = HeatingModelForm(
            request.POST,
            instance=heating
        )

        if form.is_valid():
            form.save()

            return redirect(
                "catalog:heating_detail",
                pk=heating.pk
            )

    else:
        form = HeatingModelForm(
            instance=heating
        )

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,
            "heating": heating,

            "title": "Editar Aquecimento",
            "subtitle": "Atualize as informações do aquecimento cadastrado.",

            "section_title": "Informações do aquecimento",
            "section_subtitle": "Informe o tipo, medida e valor.",

            "back_url": "catalog:heating_list",
            "breadcrumb_parent": "Aquecimento",

            "save_label": "Salvar Alterações",

            "item_type": "heating",
        }
    )


@login_required
def heating_delete(request, pk):
    heating = get_object_or_404(
        HeatingOption,
        pk=pk
    )

    deletion_error = None
    if request.method == "POST":
        try:
            heating.delete()
        except ProtectedError:
            deletion_error = "Este item est? vinculado a um or?amento e n?o pode ser exclu?do. Voc? pode desativ?-lo na edi??o."
        else:
            return redirect("catalog:heating_list")

    return render(
        request,
        "catalog/partials/confirm_delete.html",
        {
            "heating": heating,
            "deletion_error": deletion_error,
            "item": heating,
            "item_name": heating.get_type_display(),
            "item_summary": f"{heating.measure} {heating.measure_unit}",
            "item_price": heating.price,
            "price_label": "Pre?o",
            "breadcrumb_parent": "Aquecimento",
            "section_title": "Informa??es do aquecimento",
            "subtitle": "Informa??es do item cadastrado no cat?logo.",
            "back_url": reverse("catalog:heating_list"),
            "update_url": reverse("catalog:heating_update", kwargs={"pk": heating.pk}),
            "delete_url": reverse("catalog:heating_delete", kwargs={"pk": heating.pk}),
        }
    )