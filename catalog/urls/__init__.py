from django.urls import include, path

from catalog.views import catalog_hub


app_name = "catalog"


urlpatterns = [
    path(
        "",
        catalog_hub,
        name="catalog_hub",
    ),

    path(
        "pools/",
        include("catalog.urls.pools"),
    ),

    path(
        "heating/",
        include("catalog.urls.heating"),
    ),

    path(
        "waterfall/",
        include("catalog.urls.waterfall"),
    ),

    path(
        "lighting/",
        include("catalog.urls.lighting"),
    ),

    path(
        "treatment/",
        include("catalog.urls.water_treatment"),
    )
]