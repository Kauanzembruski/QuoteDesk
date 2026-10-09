from django.contrib import admin
from .models import Customer
from .forms import CustomerForm


class CustomerAdminForm(CustomerForm):
    class Meta(CustomerForm.Meta):
        fields = "__all__"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    list_display = (
        "name",
        "document",
        "phone",
        "city",
        "created_at",
    )

    search_fields = (
        "name",
        "document",
        "phone",
        "email",
    )

    list_filter = (
        "city",
        "created_at",
    )
