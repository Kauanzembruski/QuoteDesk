from django.urls import path

from catalog.views.lighting import (
    lighting_detail,
    lighting_update,
)

urlpatterns = [
    path(
        "",
        lighting_detail,
        name="lighting_detail",
    ),

    path(
        "<int:pk>/edit/",
        lighting_update,
        name="lighting_update",
    ),
]