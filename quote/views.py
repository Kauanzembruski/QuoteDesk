from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models, transaction
from .models import Quote
from dashboard.models import ActivityLog
from dashboard.utils import log_activity
from datetime import timedelta
from django.utils import timezone
from .forms import QuoteModelForm, QuoteUpdateForm

@login_required
@transaction.atomic
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
            created_date = timezone.localtime(
                quote.created_at
            ).date()

            quote.valid_until = (
                created_date
                + timedelta(days=quote.validity_days)
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

        if "status" in form.errors:
            messages.error(request, "Esta alteração de status não é permitida.")
        else:
            messages.error(request, "Não foi possível salvar o orçamento. Corrija os campos indicados.")

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
@transaction.atomic
def quote_update(request, pk):

    quote = get_object_or_404(
        Quote.objects.select_for_update(),
        pk=pk
    )

    old_status = quote.status

    if quote.is_locked:
        messages.error(request, "Orçamentos cancelados ou rejeitados não podem ser alterados.")
        return redirect("quote:quote_detail", pk=quote.pk)

    if request.method == "POST":
        form = QuoteUpdateForm(
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

            quote.validity_days = 10
            quote.valid_until = (
                timezone.localdate()
                + timedelta(days=10)
            )
            quote.save()
            status_logs = {
                Quote.Status.SENT: (ActivityLog.Type.QUOTE_SENT, "enviado"),
                Quote.Status.APPROVED: (ActivityLog.Type.QUOTE_APPROVED, "aprovado"),
                Quote.Status.REJECTED: (ActivityLog.Type.QUOTE_REJECTED, "rejeitado"),
                Quote.Status.CANCELLED: (ActivityLog.Type.QUOTE_CANCELLED, "cancelado"),
            }
            activity_type, action = (
                status_logs[quote.status] if old_status != quote.status
                else (ActivityLog.Type.QUOTE_UPDATED, "atualizado")
            )
            log_activity(
                request.user,
                activity_type,
                f"Orçamento #{quote.pk} {action}",
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

        if "status" in form.errors:
            messages.error(request, "Esta alteração de status não é permitida.")
        else:
            messages.error(request, "Não foi possível salvar o orçamento. Corrija os campos indicados.")

    else:
        form = QuoteUpdateForm(
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
@transaction.atomic
def quote_delete(request, pk):
    quote = get_object_or_404(
        Quote.objects.select_for_update(),
        pk=pk
    )

    if quote.is_locked:
        messages.error(request, "Orçamentos cancelados ou rejeitados não podem ser excluídos.")
        return redirect("quote:quote_detail", pk=quote.pk)

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
