from django.urls import path
from .views import QuoteDeskLoginView

from .views import (
    logout_view,
)

app_name = "accounts"


urlpatterns = [
    path(
        "login/",
        QuoteDeskLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        logout_view,
        name="logout",
    ),
]