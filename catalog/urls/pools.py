from django.urls import path

from catalog.views import (
    pool_list,
    pool_create,
    pool_detail,
    pool_update,
    pool_delete,
)


urlpatterns = [
    path(
        "",
        pool_list,
        name="pool_list",
    ),

    path(
        "create/",
        pool_create,
        name="pool_create",
    ),

    path(
        "<int:pk>/",
        pool_detail,
        name="pool_detail",
    ),

    path(
        "<int:pk>/edit/",
        pool_update,
        name="pool_update",
    ),

    path(
        "<int:pk>/delete/",
        pool_delete,
        name="pool_delete",
    ),
]