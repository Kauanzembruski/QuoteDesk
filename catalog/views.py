from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def catalog_hub(request):
    return render(request, "catalog/catalog_home.html")