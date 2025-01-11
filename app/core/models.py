"""Database models
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


# This is a custom class for managing operations for the User model
# such as create, update, delete, etc...
class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user.
        We create this custom method to avoid the default behaviour
        of the model when adding new data. This will ensure that
        the email is normalized and the password is properly hashed.
        """

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Create and return a new superuser.
        """
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in our system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """
    Recipe object.
    We use the basic Model class for this model.
    """
    user = models.ForeignKey(
        # Uses the user model defined in the app/settings.py file
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # Define a many to many relationship with Tag model/table
    tags = models.ManyToManyField('Tag')

    # This is useful when displaying the model in the Django admin site
    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    Tag object.
    We use the basic Model class for this model.
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # Uses the user model defined in the app/settings.py file
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name