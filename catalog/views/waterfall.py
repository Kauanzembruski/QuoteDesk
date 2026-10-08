from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from dashboard.models import ActivityLog
from dashboard.utils import log_activity

from catalog.forms import WaterfallModelForm
from catalog.models import Waterfall

@login_required
def waterfall_list(request):
    order = request.GET.get("order", "model_asc")

    waterfalls = Waterfall.objects.all()

    if order == "model_desc":
        waterfalls = waterfalls.order_by("-model")

    elif order == "price_asc":
        waterfalls = waterfalls.order_by("price")

    elif order == "price_desc":
        waterfalls = waterfalls.order_by("-price")

    else:
        waterfalls = waterfalls.order_by("model")

    return render(
        request,
        "catalog/waterfall_list.html",
        {
            "waterfalls": waterfalls,

            "title": "Cascatas",
            "subtitle": "Gerencie os modelos de cascatas.",

            "create_url": "catalog:waterfall_create",
            "create_label": "Nova Cascata",

            "search_placeholder": "Buscar cascata...",

            "selected_order": order,
            "order_options": [
                ("model_asc", "Modelo A–Z"),
                ("model_desc", "Modelo Z–A"),
                ("price_asc", "Menor preço"),
                ("price_desc", "Maior preço"),
            ],
        }
    )


@login_required
def waterfall_create(request):
    if request.method == "POST":
        form = WaterfallModelForm(request.POST)

        if form.is_valid():
            waterfall = form.save()
            log_activity(
                request.user,
                ActivityLog.Type.CATALOG_UPDATED,
                "Cascata cadastrada",
                str(waterfall),
                waterfall.pk,
            )
            return redirect("catalog:waterfall_list")

    else:
        form = WaterfallModelForm()

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,

            "title": "Nova Cascata",
            "subtitle": "Cadastre uma nova cascata no catálogo.",

            "section_title": "Informações da cascata",
            "section_subtitle": "Informe o modelo e o valor.",

            "back_url": "catalog:waterfall_list",
            "breadcrumb_parent": "Cascatas",

            "save_label": "Salvar Cascata",

            "item_type": "waterfall",
        }
    )


@login_required
def waterfall_detail(request, pk):
    waterfall = get_object_or_404(
        Waterfall,
        pk=pk
    )

    return render(
        request,
        "catalog/waterfall_detail.html",
        {
            "waterfall": waterfall,
            "item": waterfall,

            "item_name": waterfall.model,
            "item_summary": waterfall.model,

            "item_price": waterfall.price,
            "price_label": "Preço",

            "breadcrumb_parent": "Cascatas",
            "section_title": "Informações da cascata",
            "subtitle": "Informações do item cadastrado no catálogo.",

            "back_url": reverse("catalog:waterfall_list"),
            "update_url": reverse(
                "catalog:waterfall_update",
                kwargs={"pk": waterfall.pk}
            ),
            "delete_url": reverse(
                "catalog:waterfall_delete",
                kwargs={"pk": waterfall.pk}
            ),
        }
    )


@login_required
def waterfall_update(request, pk):
    waterfall = get_object_or_404(
        Waterfall,
        pk=pk
    )

    if request.method == "POST":
        form = WaterfallModelForm(
            request.POST,
            instance=waterfall
        )

        if form.is_valid():
            form.save()
            log_activity(
                request.user,
                ActivityLog.Type.CATALOG_UPDATED,
                "Cascata atualizada",
                str(waterfall),
                waterfall.pk,
            )

            return redirect(
                "catalog:waterfall_detail",
                pk=waterfall.pk
            )

    else:
        form = WaterfallModelForm(
            instance=waterfall
        )

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,
            "waterfall": waterfall,

            "title": "Editar Cascata",
            "subtitle": "Atualize as informações da cascata cadastrada.",

            "section_title": "Informações da cascata",
            "section_subtitle": "Informe o modelo e o valor.",

            "back_url": "catalog:waterfall_list",
            "breadcrumb_parent": "Cascatas",

            "save_label": "Salvar Alterações",

            "item_type": "waterfall",
        }
    )


@login_required
def waterfall_delete(request, pk):
    waterfall = get_object_or_404(
        Waterfall,
        pk=pk
    )

    deletion_error = None

    if request.method == "POST":
        try:
            waterfall_id = waterfall.pk
            waterfall_name = str(waterfall)
            waterfall.delete()

        except ProtectedError:
            deletion_error = (
                "Este item está vinculado a um orçamento e não pode ser excluído. "
                "Você pode desativá-lo na edição."
            )

        else:
            log_activity(
                request.user,
                ActivityLog.Type.CATALOG_UPDATED,
                "Cascata excluída",
                waterfall_name,
                waterfall_id,
            )
            return redirect("catalog:waterfall_list")

    return render(
        request,
        "catalog/partials/confirm_delete.html",
        {
            "waterfall": waterfall,
            "deletion_error": deletion_error,

            "item": waterfall,
            "item_name": waterfall.model,
            "item_summary": waterfall.model,

            "item_price": waterfall.price,
            "price_label": "Preço",

            "breadcrumb_parent": "Cascatas",
            "section_title": "Informações da cascata",
            "subtitle": "Informações do item cadastrado no catálogo.",

            "back_url": reverse("catalog:waterfall_list"),

            "update_url": reverse(
                "catalog:waterfall_update",
                kwargs={"pk": waterfall.pk}
            ),

            "delete_url": reverse(
                "catalog:waterfall_delete",
                kwargs={"pk": waterfall.pk}
            ),
        }
    )