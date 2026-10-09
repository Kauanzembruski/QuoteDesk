from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render


from dashboard.models import ActivityLog
from dashboard.utils import log_activity

from catalog.models import WaterTreatment
from catalog.forms import TreatmentPriceForm


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
        form = TreatmentPriceForm(request.POST, instance=treatment)
        if form.is_valid():
            form.save()
            log_activity(
                request.user, ActivityLog.Type.CATALOG_UPDATED,
                "Preço do tratamento atualizado", str(treatment), treatment.pk,
            )
            messages.success(request, "Preço atualizado com sucesso.")
        else:
            for error in form.errors.get("price", []):
                messages.error(request, error)

        return redirect(
            "catalog:treatment_detail"
        )

    return redirect(
        "catalog:treatment_detail"
    )
