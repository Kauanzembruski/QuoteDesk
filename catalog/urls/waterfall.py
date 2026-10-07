from django.urls import path

from catalog.views import (
    waterfall_list,
    waterfall_create,
    waterfall_update,
    waterfall_detail,
    waterfall_delete,
)


urlpatterns = [
    path(
        "",
        waterfall_list,
        name="waterfall_list",
    ),

    
    path(
        "create/",
        waterfall_create,
        name="waterfall_create",
    ),

    path(
        "<int:pk>/",
        waterfall_detail,
        name="waterfall_detail",
    ),

    path(
        "<int:pk>/edit/",
        waterfall_update,
        name="waterfall_update",
    ),

    path(
        "<int:pk>/delete/",
        waterfall_delete,
        name="waterfall_delete",
    ),

]