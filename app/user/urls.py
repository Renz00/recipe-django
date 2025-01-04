"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

# This will be used for the reverse method
app_name = 'user'

urlpatterns = [
    # The name reverse method to access the url
    path('create/', views.CreateUserView.as_view(), name='create'),
]
