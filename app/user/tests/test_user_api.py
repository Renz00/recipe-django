"""Tests for the user API."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """
        Helper function for creating and returning a new user.
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

    def test_create_token_for_user(self):
        """
        Generates token for valid credentials.
        """
        # Insert a new user to database using the helper function
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        # Call API to generate token based on the credentials
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def create_token_bad_credentials(self):
        """
        Test that token is not generated for invalid credentials.
        """
        # Insert a new user to database using the helper function
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        # Call API to generate token based on the credentials
        payload = {
            'email': user_details['email'],
            'password': 'wrong-password'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        """
        Test that token is not generated for blank password.
        """
        # Insert a new user to database using the helper function
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        # Call API to generate token based on the credentials
        payload = {
            'email': user_details['email'],
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_user_not_exist(self):
        """
        Test that token is not generated for non-existent user.
        """
        # Call API to generate token based on the credentials
        payload = {
            'email': 'test@example.com',
            'password': '12345678'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        # Creating a test user
        self.user = create_user(
            email='test@example.com',
            password="testpass",
            name="Test Name"
        )
        self.client = APIClient()
        # Authenticate the user for the client
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                'name': self.user.name,
                'email': self.user.email
            }
        )

    def test_post_me_not_allowed(self):
        """
        Test POST method is not allowed for the ME endpoint.
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating the user profile for authenticated user.
        """
        payload = {
            'name': 'Updated name',
            'password': 'new12345678'
        }
        res = self.client.patch(ME_URL, payload)

        # Manually refresh the db data to reflect the changes
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
