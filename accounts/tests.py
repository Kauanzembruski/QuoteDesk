from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationValidationTests(TestCase):
    def test_invalid_login_and_inactive_user_cannot_authenticate(self):
        user = get_user_model().objects.create_user(username="login-test", password="test-password")
        for data in ({}, {"username": "login-test", "password": "wrong"}):
            response = self.client.post(reverse("accounts:login"), data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
            self.assertNotIn("_auth_user_id", self.client.session)
        user.is_active = False
        user.save()
        response = self.client.post(reverse("accounts:login"), {"username": "login-test", "password": "test-password"})
        self.assertTrue(response.context["form"].errors)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_post_operations_require_login(self):
        for route in ("customer:customer_create", "catalog:pool_create", "quote:quote_create"):
            with self.subTest(route=route):
                response = self.client.post(reverse(route), {})
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response.url)
