from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def catalog_hub(request):
    return render(
        request,
        "catalog/partials/catalog_home.html"
    )
