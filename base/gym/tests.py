from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LogoutTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

    def test_logout_redirect(self):
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        # Verify user is logged out
        from django.contrib.auth import get_user
        self.assertFalse(get_user(self.client).is_authenticated)
