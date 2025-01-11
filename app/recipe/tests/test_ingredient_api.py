"""
Tests for the ingredient API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='testpass12345'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)


class PublicIngredientApiTests(TestCase):
    """Test the unauthenticated ingredient API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that login is required to access the endpoint"""
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the authenticated ingredient API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients"""
        # Create 2 ingredients for testing
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Cucumber')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients created by authenticated user
        will be returned"""
        # Create ingredient for other user
        other_user = create_user(email="otheruser@example.com",
                                 password="testpass12345")
        Ingredient.objects.create(user=other_user, name='Salt')

        # Create ingredient for authenticated user
        Ingredient.objects.create(user=self.user, name='Vinegar')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that the response only contains the ingredient
        # created by the authenticated user
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)