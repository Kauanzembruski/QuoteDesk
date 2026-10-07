from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf.urls.static import static
from config import settings


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            pattern_name="accounts:login",
            permanent=False,
        ),
    ),

    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("customers/", include("customer.urls")),
    path("catalog/", include("catalog.urls")),
    path("quote/", include("quote.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )