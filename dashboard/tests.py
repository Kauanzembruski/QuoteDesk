from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class DashboardInputTests(TestCase):
    def test_invalid_months_fall_back_without_error(self):
        self.client.force_login(get_user_model().objects.create_user(username="dashboard-test"))
        current = timezone.localtime().strftime("%Y-%m")
        for month in ("", "invalid", "2026-13", "0001-01", "9999-12", "0000-01"):
            with self.subTest(month=month):
                response = self.client.get(reverse("dashboard:dashboard"), {"month": month})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["selected_month"], current)
