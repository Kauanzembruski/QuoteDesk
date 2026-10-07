from django.contrib.auth.views import LoginView


class QuoteDeskLoginView(LoginView):
    template_name = "accounts/login.html"