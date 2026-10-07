from django.urls import path

from catalog.views import (
    treatment_update,
    treatment_detail,
)

urlpatterns = [
    path(
        "",
        treatment_detail,
        name="treatment_detail",
    ),

    path(
        "<int:pk>/edit/",
        treatment_update,
        name="treatment_update",
    ),
]