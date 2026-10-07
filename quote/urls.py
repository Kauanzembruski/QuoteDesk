from django.urls import path

from .views import quote_create


app_name = "quote"

urlpatterns = [
    path(
        "new/",
        quote_create,
        name="quote_create",
    ),
]