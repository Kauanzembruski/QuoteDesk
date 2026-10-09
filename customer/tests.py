from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import PoolModel
from dashboard.models import ActivityLog
from quote.models import Quote
from .forms import CustomerForm
from .models import Customer
from .admin import CustomerAdminForm


class CustomerValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="customer-test")
        self.client.force_login(self.user)

    def data(self, **changes):
        data = dict(name="Cliente", document="123.456.789-01", phone="(11) 99999-9999",
                    email="cliente@example.com", city="Cidade", postal_code="12345-678")
        data.update(changes)
        return data

    def test_normalization_and_optional_fields(self):
        form = CustomerForm(self.data(name=" Cliente ", city=" Cidade "))
        self.assertTrue(form.is_valid(), form.errors)
        customer = form.save()
        self.assertEqual(customer.name, "Cliente")
        self.assertEqual(customer.city, "Cidade")
        self.assertEqual(customer.document, "12345678901")
        self.assertEqual(customer.phone, "11999999999")
        self.assertEqual(customer.postal_code, "12345678")
        for index in range(2):
            form = CustomerForm(self.data(name=f"Outro {index}", document="", postal_code="", email=""))
            self.assertTrue(form.is_valid(), form.errors)
            self.assertIsNone(form.save().document)

    def test_duplicate_document_with_and_without_punctuation(self):
        customer = Customer.objects.create(name="Existente", document="123.456.789-01", phone="11999999999", city="Cidade")
        for document in ("12345678901", "123.456.789-01"):
            form = CustomerForm(self.data(document=document))
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors["document"], ["Este CPF/CNPJ já está cadastrado."])
        form = CustomerForm(self.data(name="Existente"), instance=customer)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_fields_and_lengths(self):
        for field, value in (("name", " "), ("city", " "), ("document", "123"),
                             ("document", "ABC12345678901"), ("phone", "123"),
                             ("phone", "abcdefghij"), ("email", "invalid"),
                             ("postal_code", "123"), ("name", "x" * 151)):
            with self.subTest(field=field, value=value):
                form = CustomerForm(self.data(**{field: value}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)
        form = CustomerForm(self.data(email="invalid"))
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["Informe um e-mail válido."])

    def test_cnpj_and_document_search(self):
        form = CustomerForm(self.data(document="12.345.678/0001-90"))
        self.assertTrue(form.is_valid(), form.errors)
        customer = form.save()
        response = self.client.get(reverse("customer:customer_list"), {"search": "12345678"})
        self.assertContains(response, customer.name)

    def test_protected_delete_has_clear_feedback(self):
        form = CustomerForm(self.data())
        self.assertTrue(form.is_valid())
        customer = form.save()
        pool = PoolModel.objects.create(model="A", length=5, width=3, base_price=100)
        Quote.objects.create(customer=customer, pool=pool, created_by=self.user)
        response = self.client.post(reverse("customer:customer_delete", args=[customer.pk]))
        self.assertContains(response, "Este cliente está vinculado a um orçamento e não pode ser excluído.")
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())
        self.assertFalse(ActivityLog.objects.exists())

    def test_invalid_post_does_not_save_and_missing_id_is_404(self):
        response = self.client.post(reverse("customer:customer_create"), self.data(email="invalid"))
        self.assertContains(response, "Informe um e-mail válido.")
        self.assertFalse(Customer.objects.exists())
        for route in ("customer_update", "customer_delete"):
            self.assertEqual(self.client.post(reverse("customer:" + route, args=[99999]), {}).status_code, 404)

    def test_admin_shares_validation_and_preserves_neighborhood_field(self):
        form = CustomerAdminForm(self.data(document="invalid", neighborhood="Bairro"))
        self.assertIn("neighborhood", form.fields)
        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)
