from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import HeatingOption, PoolModel


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

    def test_items_used_in_quotes_cannot_be_deleted(self):
        from customer.models import Customer
        from quote.models import Quote

        customer = Customer.objects.create(name="Cliente teste", document="123", phone="123", city="Cidade")
        Quote.objects.create(customer=customer, created_by=get_user_model().objects.get(username="catalog-test"), pool=self.pool, heating=self.heating)
        for kind, item in [("pool", self.pool), ("heating", self.heating)]:
            with self.subTest(kind=kind):
                response = self.client.post(reverse(f"catalog:{kind}_delete", kwargs={"pk": item.pk}))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "vinculado a um or?amento")
                self.assertTrue(type(item).objects.filter(pk=item.pk).exists())
