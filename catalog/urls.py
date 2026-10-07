from django.urls import path
from .views import catalog_hub

app_name = "catalog"

urlpatterns = [
    path("", catalog_hub, name="catalog_hub"),
]