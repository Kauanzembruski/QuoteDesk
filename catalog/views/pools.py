from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from dashboard.models import ActivityLog
from dashboard.utils import log_activity
from catalog.forms import PoolModelForm
from catalog.models import PoolModel
from django.db.models import Q


@login_required
def pool_list(request):
    order = request.GET.get("order", "model_asc")

    pools = PoolModel.objects.all()

    if order == "model_desc":
        pools = pools.order_by("-model")

    elif order == "price_asc":
        pools = pools.order_by("base_price")

    elif order == "price_desc":
        pools = pools.order_by("-base_price")

    else:
        pools = pools.order_by("model")

    return render(
        request,
        "catalog/pool_list.html",
        {
            "pools": pools,

            "title": "Piscinas",
            "subtitle": "Gerencie os modelos de piscinas.",

            "create_url": "catalog:pool_create",
            "create_label": "Nova Piscina",

            "search_placeholder": "Buscar por modelo...",

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
def pool_create(request):
    if request.method == "POST":
        form = PoolModelForm(request.POST,request.FILES)

        if form.is_valid():
            pool = form.save()
            log_activity(
                request.user,
                ActivityLog.Type.CATALOG_UPDATED,
                "Piscina cadastrada",
                str(pool),
                pool.pk,
            )
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
            request.FILES,
            instance=pool
        )

        if form.is_valid():
            form.save()
            log_activity(
                request.user,
                ActivityLog.Type.CATALOG_UPDATED,
                "Piscina atualizada",
                str(pool),
                pool.pk,
            )

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
            "section_subtitle": "Informe o modelo, medidas, imagem e valor base.",

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
            pool_id = pool.pk
            pool_name = str(pool)
            pool.delete()
        except ProtectedError:
            deletion_error = "Este item está vinculado a um orçamento e não pode ser excluído. Você pode desativá-lo na edição."
        else:
            log_activity(
                request.user,
                ActivityLog.Type.CATALOG_UPDATED,
                "Piscina excluída",
                pool_name,
                pool_id,
            )
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