"""Test for the tags API"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
)

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url for
    read, update, and delete requests.
    This helper function will include the recipe_id in the URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create a sample user"""
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


class PublicTagsApiTest(TestCase):
    """Test unauthenticated tags API access"""

    def setUp(self):
        self.client = APIClient()

    def test_get_tag_list_auth_required(self):
        """Test that auth is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authenticated tags API access"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""

        # Creating 2 sample tags for testing
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        # Get all tags in descending alphabetical order
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the response data is equal to the serializer data
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        # Creating another user
        other_user = create_user(email="otheruser@example.com", password="testpass123")

        # Creating a tag for the other user
        Tag.objects.create(user=other_user, name="Fruity")

        # Create a tag for the authenticated user
        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Check that only one tag is returned for the authenticated user
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(res.data['name'], tag.name)

    def test_get_tag_detail(self):
        """Test retreiving a tag detail"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        url = detail_url(tag.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], tag.name)
        self.assertEqual(res.data["id"], tag.id)

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tag_exists = Tag.objects.filter(user=self.user).exists()
        self.assertFalse(tag_exists)

    def test_filter_tags_assigned_to_any_recipe(self):
        """Test only listing tags that are assigned to any recipes"""
        tag_1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag_2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_1)

        params = {'assigned_only': 1} # 1 is equivalent to True
        res = self.client.get(TAGS_URL, params)

        serial_1 = TagSerializer(tag_1)
        serial_2 = TagSerializer(tag_2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serial_1.data, res.data)
        self.assertNotIn(serial_2.data, res.data)

    def test_filtered_tags_are_unique(self):
        """TEst filtered tags do not have duplicates"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        # We dont assing this to a variable because we are only creating it
        Tag.objects.create(user=self.user, name='Lunch')
        # Create 2 recipes and assign the same tag to both
        recipe_1 = create_recipe(user=self.user)
        recipe_2 = create_recipe(user=self.user)
        recipe_1.tags.add(tag)
        recipe_2.tags.add(tag)

        params = {'assigned_only': 1} # 1 is equivalent to True
        res = self.client.get(TAGS_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)