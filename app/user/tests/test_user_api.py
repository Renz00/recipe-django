"""Tests for the user API."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return a new user.
        The spread operator is used for the parameters
        to allow for flexibility in the number of key value params.
    """
    new_user = get_user_model().objects.create_user(**params)
    return new_user


class PublicUserApiTests(TestCase):
    """
    Test the public (no auth) features of the user API
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a new user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Check if the new user exists in the database
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        # Check that the password is not returned
        # in the response for security
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists(self):
        """Test creating a user that already exists fails."""

        # Insert a new user to database using the helper function
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        create_user(**payload)

        # Create a new user with the same email as the one created above
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that the user does not exist in the database
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
