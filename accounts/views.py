from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect

class QuoteDeskLoginView(LoginView):
    template_name = "accounts/login.html"

def logout_view(request):
    logout(request)

    return redirect(
        "accounts:login"
    )