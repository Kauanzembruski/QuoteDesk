from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerForm
from customer.models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.all()

    return render(
        request,
        "customer/customer_list.html",
        {
            "customers": customers,
        }
    )

@login_required
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("customer:customer_list")

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
    customer = get_object_or_404(Customer, pk=pk)

    return render(
        request,
        "customer/customer_detail.html",
        {
            "customer": customer,
        }
    )


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():
            form.save()

            return redirect(
                "customer:customer_detail",
                pk=customer.pk
            )

    else:
        form = CustomerForm(instance=customer)

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
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer.delete()
        return redirect("customer:customer_list")

    return render(
        request,
        "customer/confirm_delete.html",
        {
            "customer": customer,
        }
    )