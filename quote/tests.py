from decimal import Decimal
from datetime import date, datetime, timezone as datetime_timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from django.urls import reverse

from catalog.models import PoolModel, HeatingOption, Lighting, Waterfall, WaterTreatment
from customer.models import Customer
from dashboard.models import ActivityLog
from .forms import QuoteModelForm
from .models import Quote


class QuoteFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="seller")
        self.editor = get_user_model().objects.create_user(username="editor")
        self.client.force_login(self.user)
        self.customer = Customer.objects.create(name="Cliente", phone="123", city="Cidade")
        self.pool = PoolModel.objects.create(model="A", length=5, width=3, base_price="1000.10")
        self.pool2 = PoolModel.objects.create(model="B", length=6, width=3, base_price="2000.20")
        self.options = {
            "heating": HeatingOption.objects.create(type="solar", measure=10, price="100.10"),
            "lighting": Lighting.objects.create(type="kit_2", price="50.10"),
            "waterfall": Waterfall.objects.create(model="A", price="30.10"),
            "water_treatment": WaterTreatment.objects.create(type="chlorine", price="20.10"),
        }

    def data(self, **changes):
        data = dict(customer=self.customer.pk, pool=self.pool.pk, status="draft", validity_days=10)
        data.update({field: option.pk for field, option in self.options.items()})
        data.update(changes)
        return data

    def create_quote(self):
        response = self.client.post(reverse("quote:quote_create"), self.data())
        self.assertEqual(response.status_code, 302)
        return Quote.objects.latest("pk")

    def update(self, quote, **changes):
        return self.client.post(reverse("quote:quote_update", args=[quote.pk]), self.data(**changes))

    def test_create_snapshots_total_and_log(self):
        quote = self.create_quote()
        self.assertEqual(quote.status, "draft")
        self.assertEqual(quote.pool_price, Decimal(self.pool.base_price))
        for field, option in self.options.items():
            self.assertEqual(getattr(quote, field + "_price"), Decimal(option.price))
        self.assertEqual(quote.total_price, Decimal("1200.50"))
        self.assertEqual(quote.created_by, self.user)
        self.assertEqual(ActivityLog.objects.get().type, "quote_created")
        self.assertContains(self.client.get(reverse("quote:quote_detail", args=[quote.pk])), "Orçamento criado com sucesso.")

    def test_creation_rejects_forged_status(self):
        for status in ("sent", "approved", "rejected", "cancelled", "invalid"):
            with self.subTest(status=status):
                response = self.client.post(reverse("quote:quote_create"), self.data(status=status))
                self.assertContains(response, "Esta alteração de status não é permitida.")
        self.assertFalse(Quote.objects.exists())
        self.assertFalse(ActivityLog.objects.exists())

    def test_every_status_transition_and_single_log(self):
        allowed = {"draft": {"sent", "cancelled"}, "sent": {"approved", "rejected", "cancelled"}}
        for old in Quote.Status.values:
            for new in [*Quote.Status.values, "invalid"]:
                with self.subTest(old=old, new=new):
                    quote = self.create_quote()
                    Quote.objects.filter(pk=quote.pk).update(status=old)
                    before = ActivityLog.objects.count()
                    response = self.update(quote, status=new, pool=self.pool2.pk)
                    quote.refresh_from_db()
                    valid = old not in ("cancelled", "rejected") and (old == new or new in allowed.get(old, set()))
                    self.assertEqual(quote.status, new if valid else old)
                    self.assertEqual(ActivityLog.objects.count(), before + int(valid))
                    if valid:
                        self.assertEqual(response.status_code, 302)
                        self.assertEqual(ActivityLog.objects.first().type, "quote_updated" if old == new else "quote_" + new)
                        self.assertContains(self.client.get(response.url), "Orçamento atualizado com sucesso.")
                    else:
                        if old in ("cancelled", "rejected"):
                            self.assertContains(self.client.get(response.url), "não podem ser alterados.")
                        else:
                            self.assertContains(response, "Esta alteração de status não é permitida.")
                        self.assertEqual(quote.pool_id, self.pool.pk)
                        self.assertEqual(quote.total_price, Decimal("1200.50"))

    def test_edit_all_options_remove_and_preserve_history(self):
        historical = self.create_quote()
        quote = self.create_quote()
        created_at = quote.created_at
        replacements = {
            "heating": HeatingOption.objects.create(type="solar", measure=20, price="200.20"),
            "lighting": Lighting.objects.create(type="kit_4", price="60.20"),
            "waterfall": Waterfall.objects.create(model="B", price="40.20"),
            "water_treatment": WaterTreatment.objects.create(type="ozone", price="30.20"),
        }
        self.client.force_login(self.editor)
        self.update(quote, pool=self.pool2.pk, created_by=self.editor.pk, created_at="2000-01-01",
                    **{field: option.pk for field, option in replacements.items()})
        quote.refresh_from_db()
        self.assertEqual(quote.pool_price, Decimal(self.pool2.base_price))
        for field, option in replacements.items():
            self.assertEqual(getattr(quote, field + "_price"), Decimal(option.price))
        self.assertEqual(quote.total_price, Decimal("2331.00"))
        self.assertEqual(quote.created_by, self.user)
        self.assertEqual(quote.created_at, created_at)
        self.update(quote, **{field: "" for field in self.options})
        quote.refresh_from_db()
        for field in self.options:
            self.assertIsNone(getattr(quote, field))
            self.assertEqual(getattr(quote, field + "_price"), 0)
        self.assertEqual(quote.total_price, Decimal(self.pool.base_price))
        historical.refresh_from_db()
        self.assertEqual(historical.total_price, Decimal("1200.50"))

    def test_current_catalog_prices_affect_only_edited_quote(self):
        historical = self.create_quote()
        quote = self.create_quote()
        PoolModel.objects.filter(pk=self.pool.pk).update(base_price="1500.10")
        for option in self.options.values():
            type(option).objects.filter(pk=option.pk).update(price="100.00")
        self.update(quote)
        quote.refresh_from_db()
        historical.refresh_from_db()
        self.assertEqual(quote.total_price, Decimal("1900.10"))
        self.assertEqual(historical.total_price, Decimal("1200.50"))

    def test_invalid_edit_shows_errors_without_saving(self):
        quote = self.create_quote()
        before = ActivityLog.objects.count()
        response = self.update(quote, pool="999999")
        self.assertContains(response, "Corrija os campos indicados.")
        self.assertContains(response, "Piscina:")
        quote.refresh_from_db()
        self.assertEqual(quote.pool_id, self.pool.pk)
        self.assertEqual(ActivityLog.objects.count(), before)

    def test_validation_even_if_choices_are_bypassed(self):
        quote = self.create_quote()
        quote.status = "sent"
        form = QuoteModelForm(self.data(status="draft"), instance=quote)
        form.fields["status"].choices = Quote.Status.choices
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_creation_statuses_and_approved_dashboard(self):
        response = self.client.get(reverse("quote:quote_create"))
        self.assertNotContains(response, '<option value="approved">Aprovado</option>', html=True)
        quote = self.create_quote()
        self.update(quote, status="sent")
        response = self.client.get(reverse("quote:quote_update", args=[quote.pk]))
        self.assertContains(response, '<option value="approved">Aprovado</option>', html=True)
        self.assertContains(response, '<option value="rejected">Rejeitado</option>', html=True)
        self.update(quote, status="approved")
        dashboard = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(dashboard.context["approved_quotes"], 1)
        self.assertEqual(dashboard.context["approved_value"], Decimal("1200.50"))
        self.assertEqual(sum(dashboard.context["chart_values"]), 1)
        self.assertAlmostEqual(sum(dashboard.context["chart_amounts"]), 1200.50)

    def test_required_customer_and_pool(self):
        for field in ("customer", "pool"):
            with self.subTest(field=field):
                response = self.client.post(reverse("quote:quote_create"), self.data(**{field: ""}))
                self.assertIn(field, response.context["form"].errors)
                self.assertFalse(Quote.objects.exists())

    def test_inactive_and_nonexistent_catalog_ids_create_and_update(self):
        quote = self.create_quote()
        items = {"pool": self.pool, **self.options}
        for field, item in items.items():
            type(item).objects.filter(pk=item.pk).update(active=False)
            for url in (reverse("quote:quote_create"), reverse("quote:quote_update", args=[quote.pk])):
                for value in (item.pk, "999999", "invalid"):
                    with self.subTest(field=field, url=url, value=value):
                        before = ActivityLog.objects.count()
                        response = self.client.post(url, self.data(**{field: value}))
                        self.assertIn(field, response.context["form"].errors)
                        if value == item.pk:
                            self.assertContains(response, "Este item está inativo e não pode ser selecionado.")
                        self.assertEqual(Quote.objects.count(), 1)
                        self.assertEqual(ActivityLog.objects.count(), before)
            type(item).objects.filter(pk=item.pk).update(active=True)
        quote.refresh_from_db()
        self.assertEqual(quote.total_price, Decimal("1200.50"))

    def test_manual_total_is_ignored_and_overflow_is_rejected(self):
        response = self.client.post(reverse("quote:quote_create"), self.data(total_price="0", pool_price="0"))
        self.assertEqual(response.status_code, 302)
        quote = Quote.objects.get()
        self.assertEqual(quote.total_price, Decimal("1200.50"))
        PoolModel.objects.filter(pk=self.pool.pk).update(base_price="99999999.99")
        response = self.update(quote)
        self.assertContains(response, "O total do orçamento excede o limite permitido.")
        quote.refresh_from_db()
        self.assertEqual(quote.total_price, Decimal("1200.50"))

    def test_legacy_invalid_catalog_type_cannot_be_selected(self):
        item = Lighting.objects.create(type="legacy", price=1, active=True)
        response = self.client.post(reverse("quote:quote_create"), self.data(lighting=item.pk))
        self.assertIn("lighting", response.context["form"].errors)
        self.assertFalse(Quote.objects.exists())
        self.assertFalse(ActivityLog.objects.exists())

    def test_cancelled_and_rejected_block_form_edit_and_delete(self):
        for status in ("cancelled", "rejected"):
            with self.subTest(status=status):
                quote = self.create_quote()
                Quote.objects.filter(pk=quote.pk).update(status=status)
                quote.refresh_from_db()
                before = ActivityLog.objects.count()
                form = QuoteModelForm(self.data(status=status), instance=quote)
                self.assertFalse(form.is_valid())
                self.assertIn("não podem ser alterados", str(form.non_field_errors()))
                for route in ("quote_update", "quote_delete"):
                    url = reverse("quote:" + route, args=[quote.pk])
                    self.assertEqual(self.client.get(url).status_code, 302)
                    self.assertEqual(self.client.post(url, self.data(status=status)).status_code, 302)
                quote.refresh_from_db()
                self.assertEqual(quote.status, status)
                self.assertEqual(quote.total_price, Decimal("1200.50"))
                self.assertEqual(ActivityLog.objects.count(), before)

    def test_delete_log_and_feedback(self):
        quote = self.create_quote()
        response = self.client.post(reverse("quote:quote_delete", args=[quote.pk]), follow=True)
        self.assertContains(response, "Orçamento excluído com sucesso.")
        self.assertFalse(Quote.objects.filter(pk=quote.pk).exists())
        self.assertEqual(ActivityLog.objects.first().type, "quote_deleted")

    def test_list_detail_and_dashboard_statuses(self):
        for status in Quote.Status.values:
            quote = self.create_quote()
            Quote.objects.filter(pk=quote.pk).update(status=status)
            quote.refresh_from_db()
            response = self.client.get(reverse("quote:quote_list"), {"status": status})
            self.assertEqual(list(response.context["quotes"]), [quote])
            self.assertContains(response, quote.get_status_display())
            self.assertContains(self.client.get(reverse("quote:quote_detail", args=[quote.pk])), quote.get_status_display())
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(response.context["total_quotes"], 5)
        self.assertEqual(response.context["approved_quotes"], 1)
        self.assertEqual(response.context["pending_quotes"], 2)
        self.assertEqual(response.context["approved_value"], Decimal("1200.50"))
        self.assertEqual({q.status for q in response.context["pending_list"]}, {"draft", "sent"})

    def test_quote_and_log_are_atomic(self):
        quote = self.create_quote()
        with patch("quote.views.log_activity", side_effect=RuntimeError("log failed")):
            with self.assertRaises(RuntimeError):
                self.update(quote, status="sent")
        quote.refresh_from_db()
        self.assertEqual(quote.status, "draft")
        self.assertEqual(ActivityLog.objects.count(), 1)


class QuoteExpirationTests(SimpleTestCase):
    def expired(self, status="draft", valid_until=date(2026, 10, 18)):
        quote = Quote(status=status, valid_until=valid_until)
        with patch("quote.models.timezone.localdate", return_value=date(2026, 10, 19)):
            return quote.is_expired

    def test_without_valid_until(self):
        self.assertFalse(self.expired(valid_until=None))

    def test_valid_until_today_is_not_expired(self):
        self.assertFalse(self.expired(valid_until=date(2026, 10, 19)))

    def test_draft_expired_yesterday(self):
        self.assertTrue(self.expired(status=Quote.Status.DRAFT))

    def test_sent_expired_yesterday(self):
        self.assertTrue(self.expired(status=Quote.Status.SENT))

    def test_approved_is_not_expired(self):
        self.assertFalse(self.expired(status=Quote.Status.APPROVED))

    def test_rejected_is_not_expired(self):
        self.assertFalse(self.expired(status=Quote.Status.REJECTED))

    def test_cancelled_is_not_expired(self):
        self.assertFalse(self.expired(status=Quote.Status.CANCELLED))

    def test_future_validity_is_not_expired(self):
        self.assertFalse(self.expired(valid_until=date(2026, 10, 20)))

    def test_uses_local_day_in_active_timezone(self):
        quote = Quote(status=Quote.Status.SENT, valid_until=date(2026, 10, 18))
        with timezone.override("America/Sao_Paulo"):
            with patch("django.utils.timezone.now", return_value=datetime(2026, 10, 19, 2, 59, tzinfo=datetime_timezone.utc)):
                self.assertFalse(quote.is_expired)
            with patch("django.utils.timezone.now", return_value=datetime(2026, 10, 19, 3, 0, tzinfo=datetime_timezone.utc)):
                self.assertTrue(quote.is_expired)


class QuoteExpirationDisplayTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="expiration-test")
        self.client.force_login(user)
        customer = Customer.objects.create(name="Cliente validade", phone="11999999999", city="Cidade")
        pool = PoolModel.objects.create(model="Validade", length=5, width=3, base_price=100)
        self.quote = Quote.objects.create(customer=customer, created_by=user, pool=pool,
                                          pool_price=100, status="sent", validity_days=10,
                                          valid_until=date(2026, 10, 18))

    def pages(self):
        return (
            reverse("quote:quote_detail", args=[self.quote.pk]),
            reverse("quote:quote_list"),
            reverse("dashboard:dashboard"),
        )

    def test_expiration_display_preserves_status_metrics_and_logs(self):
        original_updated_at = self.quote.updated_at
        with patch("quote.models.timezone.localdate", return_value=date(2026, 10, 19)):
            for url in self.pages():
                response = self.client.get(url)
                self.assertContains(response, "Enviado")
                self.assertContains(response, '>Expirado</span>')
                if url == self.pages()[0]:
                    self.assertContains(response, "Validade: Expirada em 18/10/2026")
                if url == self.pages()[2]:
                    self.assertEqual(response.context["pending_quotes"], 1)
                    self.assertEqual(response.context["total_quotes"], 1)
                    self.assertEqual(response.context["approved_quotes"], 0)
                    self.assertEqual(list(response.context["pending_list"]), [self.quote])
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.status, Quote.Status.SENT)
        self.assertEqual(self.quote.updated_at, original_updated_at)
        self.assertEqual(self.quote.total_price, 100)
        self.assertFalse(ActivityLog.objects.exists())

    def test_valid_today_display(self):
        with patch("quote.models.timezone.localdate", return_value=date(2026, 10, 18)):
            for url in self.pages():
                response = self.client.get(url)
                self.assertNotContains(response, '>Expirado</span>')
                if url == self.pages()[0]:
                    self.assertContains(response, "10 dias · válido até 18/10/2026")

    def test_final_status_display_and_missing_validity(self):
        for status in (Quote.Status.APPROVED, Quote.Status.REJECTED, Quote.Status.CANCELLED):
            Quote.objects.filter(pk=self.quote.pk).update(status=status)
            with patch("quote.models.timezone.localdate", return_value=date(2026, 10, 19)):
                for url in self.pages():
                    self.assertNotContains(self.client.get(url), '>Expirado</span>')
        Quote.objects.filter(pk=self.quote.pk).update(valid_until=None)
        response = self.client.get(self.pages()[0])
        self.assertContains(response, "Validade não informada")
