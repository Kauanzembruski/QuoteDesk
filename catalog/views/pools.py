from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import PoolModelForm
from catalog.models import PoolModel



@login_required
def pool_list(request):
    pools = PoolModel.objects.all()

    return render(
        request,
        "catalog/pool_list.html",
        {
            "pools": pools,
            "title": "Piscinas",
            "subtitle": "Gerencie os modelos de piscinas cadastrados no catálogo.",
            "create_url": "catalog:pool_create",
            "create_label": "Nova Piscina",
            "search_placeholder": "Buscar por modelo...",
        }
    )


@login_required
def pool_create(request):
    if request.method == "POST":
        form = PoolModelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("catalog:pool_list")

    else:
        form = PoolModelForm()

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,

            "title": "Nova Piscina",
            "subtitle": "Cadastre um novo modelo de piscina no catálogo.",

            "section_title": "Informações da piscina",
            "section_subtitle": "Informe o modelo, medidas e valor base.",

            "back_url": "catalog:pool_list",
            "breadcrumb_parent": "Piscinas",

            "save_label": "Salvar Piscina",

            "item_type": "pool",
        }
    )


@login_required
def pool_detail(request, pk):
    pool = get_object_or_404(
        PoolModel,
        pk=pk
    )

    return render(
        request,
        "catalog/pool_detail.html",
        {
            "pool": pool,
            "item": pool,
            "item_name": pool.model,
            "item_summary": f"{pool.length} m ? {pool.width} m",
            "item_price": pool.base_price,
            "price_label": "Pre?o Base",
            "breadcrumb_parent": "Piscinas",
            "section_title": "Informa??es da piscina",
            "subtitle": "Informa??es do item cadastrado no cat?logo.",
            "back_url": reverse("catalog:pool_list"),
            "update_url": reverse("catalog:pool_update", kwargs={"pk": pool.pk}),
            "delete_url": reverse("catalog:pool_delete", kwargs={"pk": pool.pk}),
        }
    )

@login_required
def pool_update(request, pk):
    pool = get_object_or_404(
        PoolModel,
        pk=pk
    )

    if request.method == "POST":
        form = PoolModelForm(
            request.POST,
            instance=pool
        )

        if form.is_valid():
            form.save()

            return redirect(
                "catalog:pool_detail",
                pk=pool.pk
            )

    else:
        form = PoolModelForm(
            instance=pool
        )

    return render(
        request,
        "catalog/partials/catalog_form.html",
        {
            "form": form,
            "pool": pool,

            "title": "Editar Piscina",
            "subtitle": "Atualize as informações da piscina cadastrada.",

            "section_title": "Informações da piscina",
            "section_subtitle": "Informe o modelo, medidas e valor base.",

            "back_url": "catalog:pool_list",
            "breadcrumb_parent": "Piscinas",

            "save_label": "Salvar Alterações",

            "item_type": "pool",
        }
    )


@login_required
def pool_delete(request, pk):
    pool = get_object_or_404(
        PoolModel,
        pk=pk
    )

    deletion_error = None
    if request.method == "POST":
        try:
            pool.delete()
        except ProtectedError:
            deletion_error = "Este item est? vinculado a um or?amento e n?o pode ser exclu?do. Voc? pode desativ?-lo na edi??o."
        else:
            return redirect("catalog:pool_list")

    return render(
        request,
        "catalog/partials/confirm_delete.html",
        {
            "pool": pool,
            "deletion_error": deletion_error,
            "item": pool,
            "item_name": pool.model,
            "item_summary": f"{pool.length} m ? {pool.width} m",
            "item_price": pool.base_price,
            "price_label": "Pre?o Base",
            "breadcrumb_parent": "Piscinas",
            "section_title": "Informa??es da piscina",
            "subtitle": "Informa??es do item cadastrado no cat?logo.",
            "back_url": reverse("catalog:pool_list"),
            "update_url": reverse("catalog:pool_update", kwargs={"pk": pool.pk}),
            "delete_url": reverse("catalog:pool_delete", kwargs={"pk": pool.pk}),
        }
    )