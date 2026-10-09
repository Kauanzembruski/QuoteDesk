from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from dashboard.models import ActivityLog
from dashboard.utils import log_activity

from catalog.models import Lighting
from catalog.forms import LightingPriceForm


@login_required
def lighting_detail(request):
    kit_2, _ = Lighting.objects.get_or_create(
        type=Lighting.Type.KIT_2,
        defaults={
            "price": 0,
            "active": True,
        }
    )

    kit_4, _ = Lighting.objects.get_or_create(
        type=Lighting.Type.KIT_4,
        defaults={
            "price": 0,
            "active": True,
        }
    )

    return render(
        request,
        "catalog/lighting_detail.html",
        {
            "kit_2": kit_2,
            "kit_4": kit_4,
        }
    )


@login_required
def lighting_update(request, pk):
    lighting = get_object_or_404(
        Lighting,
        pk=pk
    )

    if request.method == "POST":
        form = LightingPriceForm(request.POST, instance=lighting)
        if form.is_valid():
            form.save()
            log_activity(
                request.user, ActivityLog.Type.CATALOG_UPDATED,
                "Preço da iluminação atualizado", str(lighting), lighting.pk,
            )
            messages.success(request, "Preço atualizado com sucesso.")
        else:
            for error in form.errors.get("price", []):
                messages.error(request, error)

    return redirect("catalog:lighting_detail")
