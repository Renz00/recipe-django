"""Tests for the django admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Tests for django admin site"""

    # this method should be camel case for some reason.
    # This method is called before each test
    def setUp(self):
        """Create user a client.
        """
        self.client = Client()
        # Create a super user for testing
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123"
        )
        # Authenticate client with the super user
        self.client.force_login(self.admin_user)
        # Create a regular user for testing
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123"
        )

    def test_users_list(self):
        """Test that users are listed on page"""
        # Getting the url for the core_user_changelist function/method
        url = reverse('admin:core_user_changelist')
        # getting the response from the url
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that the edit user page works.
        """
        # Getting the url with an argument of the authenticated user id
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works.
        """
        user = reverse('admin:core_user_add')
        res = self.client.get(user)

        self.assertEqual(res.status_code, 200)
