from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


from dashboard.models import ActivityLog
from dashboard.utils import log_activity

from catalog.models import WaterTreatment


@login_required
def treatment_detail(request):
    chlorine, _ = WaterTreatment.objects.get_or_create(
        type="chlorine",
        defaults={
            "price": 0,
            "active": True,
        }
    )

    ozone, _ = WaterTreatment.objects.get_or_create(
        type="ozone",
        defaults={
            "price": 0,
            "active": True,
        }
    )

    return render(
        request,
        "catalog/treatment_detail.html",
        {
            "chlorine": chlorine,
            "ozone": ozone,
        }
    )


@login_required
def treatment_update(request, pk):
    treatment = get_object_or_404(
        WaterTreatment,
        pk=pk
    )

    if request.method == "POST":
        price = request.POST.get("price")

        treatment.price = price
        treatment.save()
        log_activity(
            request.user,
            ActivityLog.Type.CATALOG_UPDATED,
            "Preço do tratamento atualizado",
            str(treatment),
            treatment.pk,
        )

        return redirect(
            "catalog:treatment_detail"
        )

    return redirect(
        "catalog:treatment_detail"
    )