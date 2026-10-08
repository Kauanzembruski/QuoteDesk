from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .forms import QuoteModelForm
from .models import Quote
from dashboard.models import ActivityLog
from dashboard.utils import log_activity

@login_required
def quote_create(request):

    if request.method == "POST":
        form = QuoteModelForm(request.POST)

        if form.is_valid():
            quote = form.save(commit=False)

            quote.created_by = request.user

            quote.pool_price = quote.pool.base_price

            quote.heating_price = (
                quote.heating.price
                if quote.heating
                else 0
            )

            quote.lighting_price = (
                quote.lighting.price
                if quote.lighting
                else 0
            )

            quote.waterfall_price = (
                quote.waterfall.price
                if quote.waterfall
                else 0
            )

            quote.water_treatment_price = (
                quote.water_treatment.price
                if quote.water_treatment
                else 0
            )

            quote.save()
            log_activity(
                request.user,
                ActivityLog.Type.QUOTE_CREATED,
                f"Orçamento #{quote.pk} criado",
                f"Cliente: {quote.customer}",
                quote.pk,
            )
            messages.success(
                request,
                "Orçamento criado com sucesso."
            )

            return redirect(
                "quote:quote_detail",
                pk=quote.pk
            )

    else:
        form = QuoteModelForm()

    return render(
        request,
        "quote/quote_form.html",
        {
            "form": form,
        }
    )


@login_required
def quote_detail(request, pk):

    quote = get_object_or_404(
        Quote,
        pk=pk
    )

    return render(
        request,
        "quote/quote_detail.html",
        {
            "quote": quote,
        }
    )


@login_required
def quote_list(request):
    quotes = (
        Quote.objects
        .select_related(
            "customer",
            "pool",
            "created_by",
        )
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "")
    order = request.GET.get("order", "recent")

    if search:
        quotes = quotes.filter(
            models.Q(customer__name__icontains=search)
            | models.Q(pool__model__icontains=search)
            | models.Q(pk__icontains=search)
        )

    if status:
        quotes = quotes.filter(status=status)

    if order == "oldest":
        quotes = quotes.order_by("created_at")
    else:
        quotes = quotes.order_by("-created_at")

    return render(
        request,
        "quote/quote_list.html",
        {
            "quotes": quotes,
            "search": search,
            "selected_status": status,
            "selected_order": order,
            "status_choices": Quote.Status.choices,
        }
    )

@login_required
def quote_update(request, pk):

    quote = get_object_or_404(
        Quote,
        pk=pk
    )

    old_status = quote.status

    if request.method == "POST":
        form = QuoteModelForm(
            request.POST,
            instance=quote
        )

        if form.is_valid():
            quote = form.save(commit=False)

            quote.pool_price = quote.pool.base_price

            quote.heating_price = (
                quote.heating.price
                if quote.heating
                else 0
            )

            quote.lighting_price = (
                quote.lighting.price
                if quote.lighting
                else 0
            )

            quote.waterfall_price = (
                quote.waterfall.price
                if quote.waterfall
                else 0
            )

            quote.water_treatment_price = (
                quote.water_treatment.price
                if quote.water_treatment
                else 0
            )

            quote.save()
            if (
                old_status != quote.status
                and quote.status == Quote.Status.APPROVED
            ):
                log_activity(
                    request.user,
                    ActivityLog.Type.QUOTE_APPROVED,
                    f"Orçamento #{quote.pk} aprovado",
                    f"Cliente: {quote.customer}",
                    quote.pk,
                )

            elif (
                old_status != quote.status
                and quote.status == Quote.Status.SENT
            ):
                log_activity(
                    request.user,
                    ActivityLog.Type.QUOTE_SENT,
                    f"Orçamento #{quote.pk} enviado",
                    f"Cliente: {quote.customer}",
                    quote.pk,
                )

            else:
                log_activity(
                    request.user,
                    ActivityLog.Type.QUOTE_UPDATED,
                    f"Orçamento #{quote.pk} atualizado",
                    f"Cliente: {quote.customer}",
                    quote.pk,
                )
            

            messages.success(
                request,
                "Orçamento atualizado com sucesso."
            )

            return redirect(
                "quote:quote_detail",
                pk=quote.pk
            )

    else:
        form = QuoteModelForm(
            instance=quote
        )

    return render(
        request,
        "quote/quote_update.html",
        {
            "form": form,
            "quote": quote,
        }
    )

@login_required
def quote_delete(request, pk):
    quote = get_object_or_404(
        Quote,
        pk=pk
    )

    if request.method == "POST":

        quote_id = quote.pk
        customer_name = str(quote.customer)
        quote.delete()

        log_activity(
            request.user,
            ActivityLog.Type.QUOTE_DELETED,
            f"Orçamento #{quote_id} excluído",
            f"Cliente: {customer_name}",
            quote_id,
        )
        messages.success(
            request,
            "Orçamento excluído com sucesso."
        )

        return redirect(
            "quote:quote_list"
        )

    return render(
        request,
        "quote/quote_confirm_delete.html",
        {
            "quote": quote,
        }
    )