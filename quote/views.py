from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import QuoteModelForm


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