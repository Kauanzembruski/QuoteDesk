from calendar import monthrange
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from quote.models import Quote
from dashboard.models import ActivityLog


MONTH_NAMES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


@login_required
def dashboard(request):

    now = timezone.localtime()

    selected_month = request.GET.get(
        "month",
        f"{now.year}-{now.month:02d}"
    )

    try:
        selected_date = datetime.strptime(
            selected_month,
            "%Y-%m"
        )

        selected_year = selected_date.year
        selected_month_number = selected_date.month
        if not 2 <= selected_year <= 9998:
            raise ValueError("Ano fora do intervalo suportado")

    except ValueError:
        selected_year = now.year
        selected_month_number = now.month

        selected_month = (
            f"{selected_year}-"
            f"{selected_month_number:02d}"
        )


    # ==========================================
    # MESES DO SELECT
    # ==========================================

    months = []

    year = now.year
    month = now.month

    for _ in range(12):

        months.append(
            (
                f"{year}-{month:02d}",
                f"{MONTH_NAMES[month]} de {year}"
            )
        )

        month -= 1

        if month == 0:
            month = 12
            year -= 1


    # ==========================================
    # PERÍODO SELECIONADO
    # ==========================================

    last_day = monthrange(
        selected_year,
        selected_month_number
    )[1]

    start_date = timezone.make_aware(
        datetime(
            selected_year,
            selected_month_number,
            1
        )
    )

    end_date = timezone.make_aware(
        datetime(
            selected_year,
            selected_month_number,
            last_day,
            23,
            59,
            59
        )
    )


    # ==========================================
    # ORÇAMENTOS DO MÊS
    # ==========================================

    month_quotes = Quote.objects.filter(
        created_at__range=(
            start_date,
            end_date
        )
    )


    # ==========================================
    # CARDS
    # ==========================================

    total_quotes = month_quotes.count()

    approved_quotes = month_quotes.filter(
        status=Quote.Status.APPROVED
    ).count()

    pending_quotes = month_quotes.filter(
        status__in=[
            Quote.Status.DRAFT,
            Quote.Status.SENT,
        ]
    ).count()

    approved_value = (
        month_quotes
        .filter(
            status=Quote.Status.APPROVED
        )
        .aggregate(
            total=Sum("total_price")
        )["total"]
        or 0
    )


    # ==========================================
    # ORÇAMENTOS PENDENTES
    # ==========================================

    pending_list = (
        Quote.objects
        .filter(
            status__in=[
                Quote.Status.DRAFT,
                Quote.Status.SENT,
            ]
        )
        .select_related(
            "customer",
            "pool",
            "created_by",
        )
        .order_by("-updated_at")[:5]
    )


    # ==========================================
    # GRÁFICO
    # ==========================================

    year_quotes = Quote.objects.filter(
        created_at__year=selected_year
    )

    monthly_data = (
        year_quotes
        .annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(
            quantity=Count("id"),
            amount=Sum("total_price"),
        )
        .order_by("month")
    )

    monthly_map = {}

    for item in monthly_data:

        month_number = item["month"].month

        monthly_map[month_number] = {
            "quantity": item["quantity"],
            "amount": float(
                item["amount"] or 0
            ),
        }


    chart_labels = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ]

    chart_values = []
    chart_amounts = []

    for month_number in range(1, 13):

        data = monthly_map.get(
            month_number,
            {
                "quantity": 0,
                "amount": 0,
            }
        )

        chart_values.append(
            data["quantity"]
        )

        chart_amounts.append(
            data["amount"]
        )


    # ==========================================
    # ATIVIDADE REAL DO USUÁRIO LOGADO
    # ==========================================

    recent_activities = (
        ActivityLog.objects
        .filter(
            user=request.user
        )
        .select_related("user")
        .order_by("-created_at")[:6]
    )


    # ==========================================
    # CONTEXTO
    # ==========================================

    context = {
        "months": months,
        "selected_month": selected_month,

        "total_quotes": total_quotes,
        "approved_quotes": approved_quotes,
        "pending_quotes": pending_quotes,
        "approved_value": approved_value,

        "pending_list": pending_list,

        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "chart_amounts": chart_amounts,

        "recent_activities": recent_activities,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )
