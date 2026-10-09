from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import HeatingOption, PoolModel
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from catalog.forms import PoolModelForm, HeatingModelForm, WaterfallModelForm, LightingModelForm
from catalog.models import Lighting, Waterfall, WaterTreatment
from dashboard.models import ActivityLog


class CatalogTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user(username="catalog-test", password="test-password"))
        self.pool = PoolModel.objects.create(model="Modelo teste", length="6.00", width="3.00", base_price="10000.00")
        self.heating = HeatingOption.objects.create(type="heat_exchanger", measure="30000.00", price="5000.00")

    def test_product_pages_and_actions(self):
        for kind, item, expected in [("pool", self.pool, "Modelo teste"), ("heating", self.heating, "BTU")]:
            for action in ["list", "detail", "update", "delete"]:
                with self.subTest(kind=kind, action=action):
                    url = reverse(f"catalog:{kind}_{action}", kwargs={"pk": item.pk} if action != "list" else None)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)
                    if action != "update":
                        self.assertContains(response, expected)
            response = self.client.get(reverse(f"catalog:{kind}_list"))
            self.assertContains(response, reverse(f"catalog:{kind}_detail", kwargs={"pk": item.pk}))
            self.assertContains(response, reverse(f"catalog:{kind}_delete", kwargs={"pk": item.pk}))

    def test_forms_show_correct_fields_and_validation(self):
        for kind, field, absent in [("pool", "model", "type"), ("heating", "type", "length")]:
            with self.subTest(kind=kind):
                url = reverse(f"catalog:{kind}_create")
                response = self.client.get(url)
                self.assertContains(response, f'name="{field}"')
                self.assertNotContains(response, f'name="{absent}"')
                response = self.client.post(url, {})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertContains(response, 'role="alert"')

    def test_create_update_and_delete_heating(self):
        response = self.client.post(reverse("catalog:heating_create"), {"type": "solar", "measure": "20", "price": "2000", "active": "on"})
        self.assertRedirects(response, reverse("catalog:heating_list"))
        item = HeatingOption.objects.get(type="solar")
        response = self.client.get(reverse("catalog:heating_detail", kwargs={"pk": item.pk}))
        self.assertContains(response, "20.00 m")
        response = self.client.post(reverse("catalog:heating_update", kwargs={"pk": item.pk}), {"type": "solar", "measure": "25", "price": "2500", "active": "on"})
        self.assertRedirects(response, reverse("catalog:heating_detail", kwargs={"pk": item.pk}))
        item.refresh_from_db()
        self.assertEqual(item.measure, 25)
        response = self.client.post(reverse("catalog:heating_delete", kwargs={"pk": item.pk}))
        self.assertRedirects(response, reverse("catalog:heating_list"))
        self.assertFalse(HeatingOption.objects.filter(pk=item.pk).exists())

    def test_empty_heating_list(self):
        self.heating.delete()
        self.assertContains(self.client.get(reverse("catalog:heating_list")), "Nenhum aquecimento cadastrado.")

    def test_negative_prices_and_invalid_measures_in_forms(self):
        cases = [
            (PoolModelForm, dict(model="B", length=5, width=3, base_price=100), ("length", "width", "base_price")),
            (HeatingModelForm, dict(type="solar", measure=10, price=100), ("measure", "price")),
            (WaterfallModelForm, dict(model="B", price=100), ("price",)),
            (LightingModelForm, dict(type="kit_2", price=100), ("price",)),
        ]
        for form_class, data, fields in cases:
            for field in fields:
                for value in (-1, 0) if field in ("length", "width", "measure") else (-1,):
                    with self.subTest(form=form_class, field=field, value=value):
                        form = form_class({**data, field: value})
                        self.assertFalse(form.is_valid())
                        self.assertIn(field, form.errors)
        response = self.client.post(reverse("catalog:pool_create"), dict(model="B", length=0, width=3, base_price=-1))
        self.assertContains(response, "O valor não pode ser negativo.")
        self.assertContains(response, "A medida deve ser maior que zero.")
        self.assertEqual(PoolModel.objects.count(), 1)

    def test_uniqueness_and_forged_types(self):
        for form in (
            PoolModelForm(dict(model=self.pool.model, length=6, width=3, base_price=1)),
            HeatingModelForm(dict(type="heat_exchanger", measure=30000, price=1)),
            LightingModelForm(dict(type="invalid", price=1)),
        ):
            self.assertFalse(form.is_valid())
        Lighting.objects.create(type="kit_2", price=1)
        self.assertFalse(LightingModelForm(dict(type="kit_2", price=2)).is_valid())
        Waterfall.objects.create(model="Duplicado", price=1)
        self.assertFalse(WaterfallModelForm(dict(model=" Duplicado ", price=2)).is_valid())
        WaterTreatment.objects.create(type="chlorine", price=1)
        with self.assertRaises(ValidationError):
            WaterTreatment(type="chlorine", price=2).full_clean()

    def test_fixed_price_views_reject_invalid_values_without_logs(self):
        for kind, model, item_type in (("lighting", Lighting, "kit_2"), ("treatment", WaterTreatment, "chlorine")):
            item = model.objects.create(type=item_type, price=10, active=False)
            url = reverse(f"catalog:{kind}_update", args=[item.pk])
            for value in ("-1", "", "invalid", "NaN", "Infinity", "100000000", "1.234"):
                with self.subTest(kind=kind, price=value):
                    response = self.client.post(url, {"price": value, "type": "invalid", "active": "on"}, follow=True)
                    self.assertContains(response, 'role="alert"')
                    item.refresh_from_db()
                    self.assertEqual(item.price, 10)
                    self.assertFalse(item.active)
                    self.assertEqual(item.type, item_type)
                    self.assertFalse(ActivityLog.objects.exists())
            response = self.client.post(url, {"price": "12.34", "type": "invalid", "active": "on"}, follow=True)
            self.assertContains(response, "Preço atualizado com sucesso.")
            item.refresh_from_db()
            self.assertEqual(item.price, Decimal("12.34"))
            self.assertFalse(item.active)
            self.assertEqual(item.type, item_type)
            self.assertEqual(ActivityLog.objects.count(), 1)
            ActivityLog.objects.all().delete()
            self.assertEqual(self.client.post(reverse(f"catalog:{kind}_update", args=[99999]), {"price": 1}).status_code, 404)

    def test_treatment_forms_post_to_update_routes(self):
        response = self.client.get(reverse("catalog:treatment_detail"))
        for item in WaterTreatment.objects.all():
            self.assertContains(response, f'action="{reverse("catalog:treatment_update", args=[item.pk])}"')

    def test_numeric_constraints_protect_direct_database_writes(self):
        lighting = Lighting.objects.create(type="kit_2", price=1)
        waterfall = Waterfall.objects.create(model="A", price=1)
        treatment = WaterTreatment.objects.create(type="chlorine", price=1)
        cases = [(self.pool, "base_price", -1), (self.pool, "length", 0), (self.pool, "width", -1),
                 (self.heating, "price", -1), (self.heating, "measure", 0),
                 (lighting, "price", -1), (waterfall, "price", -1), (treatment, "price", -1)]
        for item, field, value in cases:
            with self.subTest(model=type(item), field=field):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    type(item).objects.filter(pk=item.pk).update(**{field: value})

    def test_items_used_in_quotes_cannot_be_deleted(self):
        from customer.models import Customer
        from quote.models import Quote

        customer = Customer.objects.create(name="Cliente teste", document="123", phone="123", city="Cidade")
        Quote.objects.create(customer=customer, created_by=get_user_model().objects.get(username="catalog-test"), pool=self.pool, heating=self.heating)
        for kind, item in [("pool", self.pool), ("heating", self.heating)]:
            with self.subTest(kind=kind):
                response = self.client.post(reverse(f"catalog:{kind}_delete", kwargs={"pk": item.pk}))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "vinculado a um orçamento")
                self.assertTrue(type(item).objects.filter(pk=item.pk).exists())
