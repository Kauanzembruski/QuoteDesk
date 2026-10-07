from django.urls import path

from catalog.views import (
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
        "edit/",
        lighting_update,
        name="lighting_update",
    ),
]