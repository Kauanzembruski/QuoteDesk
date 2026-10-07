from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from catalog.models import Lighting


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
        lighting.price = request.POST.get("price")
        lighting.save()

    return redirect("catalog:lighting_detail")