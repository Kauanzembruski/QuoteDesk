from django.urls import path

app_name = "quote"
    
from .views import (
    quote_list,
    quote_create,
    quote_detail,
    quote_update,
    quote_delete,
)

urlpatterns = [

    path(
        "",
        quote_list,
        name="quote_list",
    ),

    path(
        "new/",
        quote_create,
        name="quote_create",
    ),

    path(
        "<int:pk>/",
        quote_detail,
        name="quote_detail",
    ),

    path(
        "<int:pk>/edit/",
        quote_update,
        name="quote_update",
    ),

    path(
        "<int:pk>/delete/",
        quote_delete,
        name="quote_delete",
    ),

]