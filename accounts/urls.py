from django.urls import path
from .views import QuoteDeskLoginView


app_name = "accounts"


urlpatterns = [
    path(
        "login/",
        QuoteDeskLoginView.as_view(),
        name="login",
    ),
]