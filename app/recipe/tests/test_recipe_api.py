"""Test for the recipe API."""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

# These url names are automatically created by the drf router
RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detial URL for
        read, update, and delete requests.
        This helper function will include the recipe_id in the URL.
    """
    # These url names are automatically created by the drf router
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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


def create_user(email='user@example.com', password='pass12345'):
    """
    Create and return a user.
    """
    return get_user_model().objects.create_user(email, password)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="pass12345")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""

        # We will add two recipes to the database
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # order by id in descending order
        # to order by ascending, remove the '-' sign
        recipes = Recipe.objects.all().order_by('-id')
        # Serialize the recipe objects directly from recipe model
        # we set many=True because we are serializing a list of objects
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # compare the data from the response with the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test that only recipes for the authenticated user are returned."""

        # create a new unauthenticated user to use for recipe creation
        other_user = create_user('user2@example.com', 'user2pass123')

        # We will add two recipes to the database for the new user
        create_recipe(user=other_user)
        create_recipe(user=other_user)

        # add one for the authenticated user
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        # Serialize the recipe objects directly from recipe model
        # we set many=True because we are serializing a list of objects
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # compare the data from the response with the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # compare the data from the response with the serialized data
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""

        # We do not use the create_recipe helper function
        # because we need to only test the API
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # this will compare all values in the payload to
        # each field in the recipe object
        for k, v in payload.items():
            # getattr is used to get the value of the recipe object
            # using the key name
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test updating a recipe with patch."""

        # Used to compare to the link value in updated data
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe",
            link=original_link
        )

        # This is the url used to update the recipe
        url = detail_url(recipe.id)
        payload = {
            'title': 'New title'
        }
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        # Verify that the title value is updated
        self.assertEqual(recipe.title, payload['title'])
        # Verify that the link value and user value is not changed
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe",
            link='https://example.com/recipe.pdf',
            description='Sample description',
            time_minutes=10,
            price=Decimal('5.20')
        )

        payload = {
            'title': "Updated recipe",
            'link': 'https://example.com/updated_recipe.pdf',
            'description': 'Updated description',
            'time_minutes': 10,
            'price': Decimal('5.20')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        # this will compare all values in the payload to
        # each field in the recipe object
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_cannot_patch_user_field(self):
        """
        Test that updating the user field returns an error.
        The user field should not be updated
        when using patch for security.
        """
        # Create a new user
        other_user = create_user(email="otheruser@example.com", password="otherpass123")
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        # Update the recipe user field with the new user
        payload = {'user': other_user.id}
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Verify that the recipe does not exist in db
        recipe_exists = Recipe.objects.filter(id=recipe.id).exists()
        self.assertFalse(recipe_exists)

    def test_delete_other_users_recipe_error(self):
        """Test delete other user's recipe returns error"""
        other_user = create_user(email="otheruser@example.com", password="otherpass123")
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # Verify that the recipe still exists in db
        recipe_exists = Recipe.objects.filter(id=recipe.id).exists()
        self.assertTrue(recipe_exists)

    # We add the test for creating tags here because tags will
    # be associated with the recipe and will only be created through
    # the recipe model.
    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'tags': [
                {'name': 'Vegan'},
                {'name': 'Dinner'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # Verify that a recipe was returned
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        # Verify that there are 2 tags associated with the recipe
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            # Verify that the tags exists in the db
            tag_exists = recipe.tags.filter(name=tag['name'],
                                            user=self.user).exists()
            self.assertTrue(tag_exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags"""

        # Create 1 tag in the db for testing
        existing_tag = Tag.objects.create(user=self.user, name='Soup')
        # Associate 2 tags with the recipe.
        # One is existing and one is new.
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'tags': [
                {'name': 'Soup'},
                {'name': 'Dinner'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # Verify that a recipe was returned
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        # Verify that there are 2 tags associated with the recipe
        self.assertEqual(recipe.tags.count(), 2)
        # Verify that the existing tag is associated with the recipe
        self.assertIn(existing_tag, recipe.tags.all())
        for tag in payload['tags']:
            # Verify that the tags exists in the db
            tag_exists = recipe.tags.filter(name=tag['name'],
                                            user=self.user).exists()
            self.assertTrue(tag_exists)

    def test_create_tag_on_recipe_update(self):
        """Test creating non-existing tags on recipe update"""
        recipe = create_recipe(user=self.user)
        # We will update the tags of the recipe
        payload = {
            'tags': [
                {'name': 'Lunch'},
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload,  format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        # Verify that the tag was created in the db
        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_assign_tag_on_recipe_update(self):
        """
        Test assigning an existing tag when updating a recipe.
        """
        tag_viand = Tag.objects.create(user=self.user, name='Viand')
        recipe = create_recipe(user=self.user)
        # Adding a tag using the Tag model associate with the recipe
        recipe.tags.add(tag_viand)

        # We will update the recipe and replace tag_viand with tag_lunch
        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {
            'tags': [
                {'name': 'Lunch'},
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        # Verify that the tag was replace and no longer exists
        self.assertNotIn(tag_viand, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing all tags on recipe update"""
        tag = Tag.objects.create(user=self.user, name='Viand')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {
            'tags': []
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    # We add the test for creating ingredients here because they will
    # be associated with the recipe and will only be created through
    # the recipe model.
    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'ingredients': [
                {'name': 'Salt'},
                {'name': 'Pepper'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # Verify that a recipe was returned
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        # Verify that there are 2 ingredients associated with the recipe
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            # Verify that the ingredients exists in the db
            ingredient_exists = recipe.ingredients.filter(name=ingredient['name'],
                                                          user=self.user).exists()
            self.assertTrue(ingredient_exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a recipe with existing ingredients"""
        # Create 1 ingredient in the db for testing
        existing_ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        # Associate 2 ingredients with the recipe.
        # One is existing and one is new.
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'ingredients': [
                {'name': 'Salt'},
                {'name': 'Pepper'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # Verify that a recipe was returned
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        # Verify that there are 2 ingredients associated with the recipe
        self.assertEqual(recipe.ingredients.count(), 2)
        # Verify that the existing ingredient is associated with the recipe
        self.assertIn(existing_ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            # Verify that the ingredients exists in the db
            ingredient_exists = recipe.ingredients.filter(name=ingredient['name'],
                                                          user=self.user).exists()
            self.assertTrue(ingredient_exists)

    def test_create_ingredient_on_recipe_update(self):
        """Test creating non-existing ingredients on recipe update"""
        recipe = create_recipe(user=self.user)
        # We will update the ingredients of the recipe
        payload = {
            'ingredients': [
                {'name': 'Salt'},
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload,  format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        # Verify that the ingredient was created in the db
        new_ingredient = Ingredient.objects.get(user=self.user, name="Salt")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_assign_existing_ingredient_on_recipe_update(self):
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient_salt = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = create_recipe(user=self.user)
        # Adding an ingredient using the Ingredient model associate with the recipe
        recipe.ingredients.add(ingredient_salt)

        # We will update the recipe and replace ingredient_salt with ingredient_pepper
        ingredient_pepper = Ingredient.objects.create(user=self.user, name='Pepper')
        payload = {
            'ingredients': [
                {'name': 'Pepper'},
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_pepper, recipe.ingredients.all())
        # Verify that the ingredient was replace and no longer exists
        self.assertNotIn(ingredient_salt, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing all ingredients on recipe update"""
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {
            'ingredients': []
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags"""
        # Creating 2 recipes for testing
        recipe_1 = create_recipe(user=self.user, title='Chicken Adobo')
        recipe_2 = create_recipe(user=self.user, title='Pork Sisig')
        # Createing 2 tags, 1 for each recipe
        tag_1 = Tag.objects.create(user=self.user, name='Halal')
        tag_2 = Tag.objects.create(user=self.user, name='Filipino')
        # Assign the tags to each recipe
        recipe_1.tags.add(tag_1)
        recipe_2.tags.add(tag_2)
        # Create a recipe with no associated tags
        recipe_3 = create_recipe(user=self.user, title='Beef Caldereta')
        # The request should return all recipes asssociated
        # to the included tags in the params
        params = {'tags': f'{tag_1.id},{tag_2.id}'}
        res = self.client.get(RECIPES_URL, params)

        # Serializing the recipe objects for comparison
        serial_1 = RecipeSerializer(recipe_1)
        serial_2 = RecipeSerializer(recipe_2)
        serial_3 = RecipeSerializer(recipe_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serial_1.data, res.data)
        self.assertIn(serial_2.data, res.data)
        # Recipe 3 should not be included in the response because
        # it does not have any of the associated tags.
        self.assertNotIn(serial_3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients"""
        # Creating 2 recipes for testing
        recipe_1 = create_recipe(user=self.user, title='Chicken Adobo')
        recipe_2 = create_recipe(user=self.user, title='Beef Caldereta')
        # Creating 2 ingredients, 1 for each recipe.
        ingredient_1 = Ingredient.objects.create(user=self.user, name='Soy Sauce')
        ingredient_2 = Ingredient.objects.create(user=self.user, name='Tomato Sauce')
        # Assign the tags to each recipe
        recipe_1.ingredients.add(ingredient_1)
        recipe_2.ingredients.add(ingredient_2)
        # Creating a recipe with no ingredients
        recipe_3 = create_recipe(user=self.user, title='Pork Sisig')
        # The request should return all recipes asssociated
        # to the included ingredients in the params
        params = {'ingredients': f'{ingredient_1.id},{ingredient_2.id}'}
        res = self.client.get(RECIPES_URL, params)

        # Serialize the created recipe objects for comparison
        serial_1 = RecipeSerializer(recipe_1)
        serial_2 = RecipeSerializer(recipe_2)
        serial_3 = RecipeSerializer(recipe_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serial_1.data, res.data)
        self.assertIn(serial_2.data, res.data)
        # Recipe 3 should not be included in the response because
        self.assertNotIn(serial_3.data, res.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload API"""

    def setUp(self):
        # Runs before every test
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        # Runs after every test
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe"""
        url = image_upload_url(self.recipe.id)
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            # This will create a basic test image. Right now this
            # image is saved in memory not in storage.
            img = Image.new('RGB', (10, 10))
            # Storing the temp file as JPEG format for this test
            img.save(image_file, format="JPEG")
            # Reset pointer to beginning of file. This is needed
            # because the file is read from the end after saving.
            image_file.seek(0)

            # Upload the temp file to the url
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that the image field is in the response data
        self.assertIn('image', res.data)
        # Verify that the image was stored in the path
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_invalid_file_type(self):
        """Test uploading an invalid file type"""
        url = image_upload_url(self.recipe.id)
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt") as image_file:
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)