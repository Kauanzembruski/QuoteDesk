"""Initial regression suite: real HTTP flows and explicit ADMIN/SELLER roles.

PDF rendering is stubbed to prevent network/media access. Authorization,
template rendering and response construction still run through the real view.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import HeatingOption, Lighting, PoolModel, Waterfall, WaterTreatment
from customer.models import Customer
from dashboard.models import ActivityLog
from quote.models import Quote


class InitialData(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_user(username="admin", role=User.Role.ADMIN)
        cls.seller_a = User.objects.create_user(username="seller-a", role=User.Role.SELLER)
        cls.seller_b = User.objects.create_user(username="seller-b", role=User.Role.SELLER)
        cls.customer = Customer.objects.create(name="Cliente inicial", phone="11999999999", city="Cidade")
        cls.pool = PoolModel.objects.create(model="Inicial", length=6, width=3, base_price=Decimal("1000.10"))
        cls.options = {
            "heating": HeatingOption.objects.create(type="solar", measure=10, price=Decimal("100.10")),
            "lighting": Lighting.objects.create(type="kit_2", price=Decimal("50.10")),
            "waterfall": Waterfall.objects.create(model="Inicial", price=Decimal("30.10")),
            "water_treatment": WaterTreatment.objects.create(type="chlorine", price=Decimal("20.10")),
        }
        cls.own = cls.make_quote(cls.seller_a)
        cls.other = cls.make_quote(cls.seller_b)

    @classmethod
    def make_quote(cls, user, **changes):
        values = dict(customer=cls.customer, pool=cls.pool, created_by=user,
                      pool_price=cls.pool.base_price)
        values.update(changes)
        return Quote.objects.create(**values)

    def setUp(self):
        self.client.force_login(self.seller_a)

    def quote_data(self, **changes):
        data = dict(customer=self.customer.pk, pool=self.pool.pk, status="draft", validity_days=10)
        data.update(changes)
        return data

    def url(self, action, quote=None):
        return reverse("quote:quote_" + action, args=[(quote or self.own).pk])

    def assert_log(self, kind, user, object_id):
        log = ActivityLog.objects.get(type=kind, object_id=object_id)
        self.assertEqual(log.user, user)
        self.assertTrue(log.title)
        self.assertTrue(log.description)
        return log


class QuotePriceTests(InitialData):
    def test_total_all_optional_snapshots(self):
        for field, item in self.options.items():
            setattr(self.own, field + "_price", item.price)
        self.assertEqual(self.own.calculate_total(), Decimal("1200.50"))

    def test_total_pool_only(self):
        self.assertEqual(self.own.calculate_total(), Decimal("1000.10"))

    def test_total_some_options(self):
        self.own.heating_price = Decimal("100.10")
        self.own.waterfall_price = Decimal("30.10")
        self.assertEqual(self.own.calculate_total(), Decimal("1130.30"))

    def test_save_recalculates_persisted_decimal_total(self):
        self.own.lighting_price = Decimal("0.20")
        self.own.total_price = Decimal("999.99")
        self.own.save()
        self.own.refresh_from_db()
        self.assertEqual(self.own.total_price, Decimal("1000.30"))
        self.assertTrue(isinstance(self.own.total_price, Decimal))

    def test_catalog_changes_preserve_every_snapshot_and_total(self):
        response = self.client.post(reverse("quote:quote_create"), self.quote_data(
            **{field: item.pk for field, item in self.options.items()}))
        self.assertEqual(response.status_code, 302)
        quote = Quote.objects.latest("pk")
        expected = {field + "_price": item.price for field, item in self.options.items()}
        expected["pool_price"] = self.pool.base_price
        self.pool.base_price = Decimal("9999.99")
        self.pool.save()
        for item in self.options.values():
            item.price = Decimal("999.99")
            item.save()
        quote.refresh_from_db()
        for field, price in expected.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(quote, field), price)
        self.assertEqual(quote.total_price, Decimal("1200.50"))

    def test_create_without_options_sets_owner_draft_zero_snapshots_and_validity(self):
        response = self.client.post(reverse("quote:quote_create"), self.quote_data(created_by=self.seller_b.pk))
        quote = Quote.objects.latest("pk")
        self.assertRedirects(response, self.url("detail", quote))
        self.assertEqual(quote.created_by, self.seller_a)
        self.assertEqual(quote.status, Quote.Status.DRAFT)
        self.assertEqual(quote.validity_days, 10)
        self.assertEqual(quote.valid_until, timezone.localdate(quote.created_at) + timedelta(days=10))
        for field in self.options:
            self.assertIsNone(getattr(quote, field))
            self.assertEqual(getattr(quote, field + "_price"), Decimal("0"))
        self.assertEqual(quote.total_price, self.pool.base_price)
        self.assert_log("quote_created", self.seller_a, quote.pk)

    def test_edit_refreshes_prices_total_and_activity(self):
        self.pool.base_price = Decimal("2000.20")
        self.pool.save()
        response = self.client.post(self.url("update"), self.quote_data(lighting=self.options["lighting"].pk))
        self.assertRedirects(response, self.url("detail"))
        self.own.refresh_from_db()
        self.assertEqual(self.own.pool_price, Decimal("2000.20"))
        self.assertEqual(self.own.lighting_price, Decimal("50.10"))
        self.assertEqual(self.own.total_price, Decimal("2050.30"))
        self.assert_log("quote_updated", self.seller_a, self.own.pk)


class QuotePermissionTests(InitialData):
    def test_seller_list_contains_own(self):
        response = self.client.get(reverse("quote:quote_list"))
        self.assertIn(self.own, response.context["quotes"])

    def test_seller_list_excludes_other_seller(self):
        response = self.client.get(reverse("quote:quote_list"))
        self.assertNotIn(self.other, response.context["quotes"])

    def test_seller_cannot_read_other_detail(self):
        response = self.client.get(self.url("detail", self.other))
        self.assertIn(response.status_code, (302, 403, 404))

    def test_seller_cannot_edit_other_quote_get_or_post(self):
        for method in (self.client.get, self.client.post):
            with self.subTest(method=method.__name__):
                response = method(self.url("update", self.other), self.quote_data())
                self.assertRedirects(response, reverse("quote:quote_list"))
        self.other.refresh_from_db()
        self.assertEqual(self.other.pool_price, self.pool.base_price)
        self.assertFalse(ActivityLog.objects.exists())

    def test_seller_cannot_change_other_status_via_post(self):
        self.client.post(self.url("update", self.other), self.quote_data(status="sent"))
        self.other.refresh_from_db()
        self.assertEqual(self.other.status, Quote.Status.DRAFT)
        self.assertFalse(ActivityLog.objects.exists())

    def test_seller_cannot_delete_even_own_quote(self):
        response = self.client.post(self.url("delete"))
        self.assertRedirects(response, reverse("dashboard:dashboard"))
        self.assertTrue(Quote.objects.filter(pk=self.own.pk).exists())
        self.assertFalse(ActivityLog.objects.exists())

    def test_admin_list_and_details_include_both_sellers(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("quote:quote_list"))
        self.assertEqual(set(response.context["quotes"]), {self.own, self.other})
        for quote in (self.own, self.other):
            self.assertEqual(self.client.get(self.url("detail", quote)).context["quote"], quote)

    def test_admin_can_edit_other_seller_and_log_actor(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url("update", self.other), self.quote_data(status="sent"))
        self.assertRedirects(response, self.url("detail", self.other))
        self.other.refresh_from_db()
        self.assertEqual(self.other.status, Quote.Status.SENT)
        self.assertEqual(self.other.created_by, self.seller_b)
        self.assert_log("quote_sent", self.admin, self.other.pk)

    def test_admin_can_delete_unlocked_quote_and_log_id(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url("delete", self.other))
        self.assertRedirects(response, reverse("quote:quote_list"))
        self.assertFalse(Quote.objects.filter(pk=self.other.pk).exists())
        self.assert_log("quote_deleted", self.admin, self.other.pk)

    def test_admin_cannot_edit_or_delete_rejected_cancelled(self):
        self.client.force_login(self.admin)
        for status in (Quote.Status.REJECTED, Quote.Status.CANCELLED):
            Quote.objects.filter(pk=self.other.pk).update(status=status)
            for action in ("update", "delete"):
                with self.subTest(status=status, action=action):
                    response = self.client.post(self.url(action, self.other), self.quote_data())
                    self.assertRedirects(response, self.url("detail", self.other))
            self.other.refresh_from_db()
            self.assertEqual(self.other.status, status)
        self.assertFalse(ActivityLog.objects.exists())


class CustomerFlowPermissionTests(InitialData):
    def customer_data(self, **changes):
        data = dict(name="Novo cliente", phone="11988888888", city="Cidade", document="")
        data.update(changes)
        return data

    def test_seller_list_detail_and_create_log(self):
        self.assertEqual(self.client.get(reverse("customer:customer_list")).status_code, 200)
        response = self.client.get(reverse("customer:customer_detail", args=[self.customer.pk]))
        self.assertEqual(response.context["customer"], self.customer)
        response = self.client.post(reverse("customer:customer_create"), self.customer_data())
        self.assertRedirects(response, reverse("customer:customer_list"))
        customer = Customer.objects.get(name="Novo cliente")
        self.assertEqual(customer.phone, "11988888888")
        self.assert_log("customer_created", self.seller_a, customer.pk)

    def test_seller_update_and_log(self):
        response = self.client.post(reverse("customer:customer_update", args=[self.customer.pk]), self.customer_data())
        self.assertRedirects(response, reverse("customer:customer_detail", args=[self.customer.pk]))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Novo cliente")
        self.assert_log("customer_updated", self.seller_a, self.customer.pk)

    def test_seller_delete_blocked_without_log(self):
        customer = Customer.objects.create(name="Livre", phone="11988888888", city="Cidade")
        response = self.client.post(reverse("customer:customer_delete", args=[customer.pk]))
        self.assertRedirects(response, reverse("dashboard:dashboard"))
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())
        self.assertFalse(ActivityLog.objects.exists())

    def test_admin_delete_free_customer_and_log(self):
        self.client.force_login(self.admin)
        customer = Customer.objects.create(name="Livre", phone="11988888888", city="Cidade")
        response = self.client.post(reverse("customer:customer_delete", args=[customer.pk]))
        self.assertRedirects(response, reverse("customer:customer_list"))
        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())
        self.assert_log("customer_deleted", self.admin, customer.pk)


class CatalogPermissionTests(InitialData):
    def test_seller_can_read_all_catalog_sections(self):
        for route in ("pool_list", "heating_list", "waterfall_list", "lighting_detail", "treatment_detail"):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse("catalog:" + route)).status_code, 200)

    def test_seller_cannot_create_edit_delete_mutable_catalog(self):
        items = {"pool": self.pool, "heating": self.options["heating"], "waterfall": self.options["waterfall"]}
        for kind, item in items.items():
            original = type(item).objects.values().get(pk=item.pk)
            count = type(item).objects.count()
            for action in ("create", "update", "delete"):
                url = reverse(f"catalog:{kind}_{action}", args=[] if action == "create" else [item.pk])
                for method in (self.client.get, self.client.post):
                    with self.subTest(kind=kind, action=action, method=method.__name__):
                        response = method(url, dict(model="Invadido", length=5, width=3,
                                                    base_price=1, price=1, type="solar", measure=30))
                        self.assertRedirects(response, reverse("dashboard:dashboard"))
            self.assertEqual(type(item).objects.count(), count)
            self.assertEqual(type(item).objects.values().get(pk=item.pk), original)
        self.assertFalse(ActivityLog.objects.exists())

    def test_seller_cannot_change_fixed_catalog_prices(self):
        for kind, item in (("lighting", self.options["lighting"]), ("treatment", self.options["water_treatment"])):
            original = item.price
            response = self.client.post(reverse(f"catalog:{kind}_update", args=[item.pk]), {"price": "1.00"})
            self.assertRedirects(response, reverse("dashboard:dashboard"))
            item.refresh_from_db()
            self.assertEqual(item.price, original)
        self.assertFalse(ActivityLog.objects.exists())

    def test_admin_pool_create_edit_delete_logs(self):
        self.client.force_login(self.admin)
        data = dict(model="Livre", length=7, width=4, base_price="200.20", active="on")
        self.assertRedirects(self.client.post(reverse("catalog:pool_create"), data), reverse("catalog:pool_list"))
        item = PoolModel.objects.get(model="Livre")
        self.assert_log("catalog_updated", self.admin, item.pk)
        ActivityLog.objects.all().delete()
        data["base_price"] = "300.30"
        self.assertRedirects(self.client.post(reverse("catalog:pool_update", args=[item.pk]), data),
                             reverse("catalog:pool_detail", args=[item.pk]))
        item.refresh_from_db()
        self.assertEqual(item.base_price, Decimal("300.30"))
        self.assert_log("catalog_updated", self.admin, item.pk)
        ActivityLog.objects.all().delete()
        self.assertRedirects(self.client.post(reverse("catalog:pool_delete", args=[item.pk])), reverse("catalog:pool_list"))
        self.assertFalse(PoolModel.objects.filter(pk=item.pk).exists())
        self.assert_log("catalog_updated", self.admin, item.pk)

    def test_admin_fixed_price_update_logs(self):
        self.client.force_login(self.admin)
        for kind, item in (("lighting", self.options["lighting"]), ("treatment", self.options["water_treatment"])):
            ActivityLog.objects.all().delete()
            response = self.client.post(reverse(f"catalog:{kind}_update", args=[item.pk]), {"price": "42.42"})
            self.assertRedirects(response, reverse(f"catalog:{kind}_detail"))
            item.refresh_from_db()
            self.assertEqual(item.price, Decimal("42.42"))
            self.assert_log("catalog_updated", self.admin, item.pk)


class DashboardScopeTests(InitialData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.a_approved = cls.make_quote(cls.seller_a, status="approved", pool_price=Decimal("200.20"))
        cls.b_approved = cls.make_quote(cls.seller_b, status="approved", pool_price=Decimal("900.90"))
        cls.previous = cls.make_quote(cls.seller_a, status="sent", pool_price=Decimal("50.50"))
        current = timezone.make_aware(datetime(2026, 10, 15, 12))
        previous = timezone.make_aware(datetime(2026, 9, 15, 12))
        Quote.objects.exclude(pk=cls.previous.pk).update(created_at=current)
        Quote.objects.filter(pk=cls.previous.pk).update(created_at=previous)

    def dashboard(self, month="2026-10"):
        return self.client.get(reverse("dashboard:dashboard"), {"month": month}).context

    def test_seller_month_metrics_only_own(self):
        context = self.dashboard()
        self.assertEqual(context["total_quotes"], 2)
        self.assertEqual(context["approved_quotes"], 1)
        self.assertEqual(context["pending_quotes"], 1)
        self.assertEqual(context["approved_value"], Decimal("200.20"))

    def test_admin_month_metrics_global(self):
        self.client.force_login(self.admin)
        context = self.dashboard()
        self.assertEqual(context["total_quotes"], 4)
        self.assertEqual(context["approved_quotes"], 2)
        self.assertEqual(context["pending_quotes"], 2)
        self.assertEqual(context["approved_value"], Decimal("1101.10"))

    def test_month_filter_changes_cards(self):
        context = self.dashboard("2026-09")
        self.assertEqual(context["selected_month"], "2026-09")
        self.assertEqual(context["total_quotes"], 1)
        self.assertEqual(context["pending_quotes"], 1)
        self.assertEqual(context["approved_quotes"], 0)
        self.assertEqual(context["approved_value"], 0)

    def test_pending_list_scoped_and_currently_spans_months(self):
        self.assertEqual(set(self.dashboard()["pending_list"]), {self.own, self.previous})

    def test_seller_chart_counts_and_amounts_only_own(self):
        context = self.dashboard()
        self.assertEqual(context["chart_values"], [0] * 8 + [1, 2, 0, 0])
        self.assertEqual(context["chart_amounts"], [0] * 8 + [50.50, 1200.30, 0, 0])

    def test_admin_chart_counts_and_amounts_global(self):
        self.client.force_login(self.admin)
        context = self.dashboard()
        self.assertEqual(context["chart_values"], [0] * 8 + [1, 4, 0, 0])
        self.assertEqual(context["chart_amounts"], [0] * 8 + [50.50, 3101.30, 0, 0])

    def test_recent_activities_only_logged_in_user_including_admin(self):
        for user in (self.admin, self.seller_a, self.seller_b):
            ActivityLog.objects.create(user=user, type="quote_created", title=user.username, object_id=self.own.pk)
        for user in (self.seller_a, self.admin):
            self.client.force_login(user)
            logs = list(self.dashboard()["recent_activities"])
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].user, user)


class PdfPermissionTests(InitialData):
    def assert_pdf(self, quote):
        with patch("quote.views.HTML") as renderer:
            renderer.return_value.write_pdf.return_value = b"%PDF-1.7\n"
            response = self.client.get(self.url("pdf", quote))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(f"orcamento-{quote.pk}.pdf", response["Content-Disposition"])
        renderer.return_value.write_pdf.assert_called_once_with()

    def test_seller_own_pdf_response(self):
        self.assert_pdf(self.own)

    def test_seller_other_pdf_blocked_before_rendering(self):
        with patch("quote.views.HTML") as renderer:
            response = self.client.get(self.url("pdf", self.other))
        self.assertEqual(response.status_code, 404)
        renderer.assert_not_called()

    def test_admin_pdf_for_both_sellers(self):
        self.client.force_login(self.admin)
        for quote in (self.own, self.other):
            with self.subTest(quote=quote.pk):
                self.assert_pdf(quote)

    def test_anonymous_pdf_requires_login(self):
        self.client.logout()
        with patch("quote.views.HTML") as renderer:
            response = self.client.get(self.url("pdf"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login")))
        renderer.assert_not_called()
