from django.urls import path

from catalog.views import (
    heating_list,
    heating_create,
    heating_detail,
    heating_update,
    heating_delete,
)


urlpatterns = [
    path(
        "",
        heating_list,
        name="heating_list",
    ),

    path(
        "create/",
        heating_create,
        name="heating_create",
    ),

    path(
        "<int:pk>/",
        heating_detail,
        name="heating_detail",
    ),

    path(
        "<int:pk>/edit/",
        heating_update,
        name="heating_update",
    ),

    path(
        "<int:pk>/delete/",
        heating_delete,
        name="heating_delete",
    ),
]