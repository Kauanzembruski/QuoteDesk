from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import User


def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if request.user.role != User.Role.ADMIN:

            messages.error(
                request,
                "Você não possui permissão para realizar esta ação."
            )

            return redirect("dashboard:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper