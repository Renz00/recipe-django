"""
Tests for the ingredient API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,
)

from recipe.serializers import (
    IngredientSerializer,
)


INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass12345'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)


def create_recipe(user, **params):
    """Helper function for creating and returning a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample recipe description',
        'link': 'https://example.com/recipe.pdf'
    }
    # add the additional parameters to the defaults dict
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


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
        ingredients = Ingredient.objects.all().order_by('-id')
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

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        url = detail_url(ingredient.id)
        payload = {'name': 'Brown Sugar'}

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Lettuce"
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredient_exists = Ingredient.objects.filter(id=ingredient.id).exists()
        self.assertFalse(ingredient_exists)

    def test_filter_ingredients_assigned_to_any_recipe(self):
        """Test only listing ingredients that are assigned to any recipes"""
        # Create 2 ingredients for testing
        ingredient_1 = Ingredient.objects.create(user=self.user,
                                                 name='Soy Sauce')
        # ingredient_2 will not be assigned to any recipe
        ingredient_2 = Ingredient.objects.create(user=self.user,
                                                 name='Vinegar')
        # Create a recipe with ingredient_1
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_1)
        recipe.refresh_from_db()

        params = {'assigned_only': 1} # 1 is equivalent to True
        res = self.client.get(INGREDIENTS_URL, params)

        serial_1 = IngredientSerializer(ingredient_1)
        serial_2 = IngredientSerializer(ingredient_2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify that only 1 ingredient is returned in response
        self.assertEqual(len(res.data), 1)
        self.assertIn(serial_1.data, res.data)
        # Verify that ingredient_2 is not included in the response
        self.assertNotIn(serial_2.data, res.data)

    def test_filtered_ingredients_are_unique(self):
        """Test that the filtered ingredients have no duplicates."""
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        # Not assign to a variable because we only need to create it
        Ingredient.objects.create(user=self.user, name='Pepper')
        # Creating 2 recipes and assigning the same ingredient to both
        recipe_1 = create_recipe(user=self.user)
        recipe_2 = create_recipe(user=self.user)
        recipe_1.ingredients.add(ingredient)
        recipe_2.ingredients.add(ingredient)

        params = {'assigned_only': 1}
        res = self.client.get(INGREDIENTS_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify that only 1 ingredient is returned in response
        self.assertEqual(len(res.data), 1)