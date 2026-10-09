from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from .forms import CustomerForm
from customer.models import Customer

from dashboard.models import ActivityLog
from dashboard.utils import log_activity


@login_required
def customer_list(request):
    search = request.GET.get("search", "").strip()
    order = request.GET.get("order", "name_asc")

    customers = Customer.objects.all()

    if search:
        customers = customers.filter(
            Q(name__icontains=search)
            | Q(document__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )

    if order == "name_desc":
        customers = customers.order_by("-name")

    elif order == "recent":
        customers = customers.order_by("-created_at")

    elif order == "oldest":
        customers = customers.order_by("created_at")

    else:
        customers = customers.order_by("name")

    return render(
        request,
        "customer/customer_list.html",
        {
            "customers": customers,
            "search": search,
            "selected_order": order,
        }
    )


@login_required
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save()

            log_activity(
                request.user,
                ActivityLog.Type.CUSTOMER_CREATED,
                "Cliente cadastrado",
                str(customer),
                customer.pk,
            )

            return redirect(
                "customer:customer_list"
            )

    else:
        form = CustomerForm()

    return render(
        request,
        "customer/customer_form.html",
        {
            "form": form,
        },
    )


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    return render(
        request,
        "customer/customer_detail.html",
        {
            "customer": customer,
        }
    )


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    if request.method == "POST":
        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():
            customer = form.save()

            log_activity(
                request.user,
                ActivityLog.Type.CUSTOMER_UPDATED,
                "Cliente atualizado",
                str(customer),
                customer.pk,
            )

            return redirect(
                "customer:customer_detail",
                pk=customer.pk
            )

    else:
        form = CustomerForm(
            instance=customer
        )

    return render(
        request,
        "customer/customer_form.html",
        {
            "form": form,
            "customer": customer,
        }
    )


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    if request.method == "POST":

        customer_id = customer.pk
        customer_name = str(customer)

        try:
            customer.delete()
        except ProtectedError:
            return render(request, "customer/confirm_delete.html", {
                "customer": customer,
                "deletion_error": "Este cliente está vinculado a um orçamento e não pode ser excluído.",
            })

        log_activity(
            request.user,
            ActivityLog.Type.CUSTOMER_DELETED,
            "Cliente excluído",
            customer_name,
            customer_id,
        )

        return redirect(
            "customer:customer_list"
        )

    return render(
        request,
        "customer/confirm_delete.html",
        {
            "customer": customer,
        }
    )
