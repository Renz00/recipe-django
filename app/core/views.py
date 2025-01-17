"""Views for health check API"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Creating a simple API view endpoint for health check
@api_view(['GET'])
def health_check(request):
    """Returns a successful response if the API is running"""
    response_msg = {'msg': 'success'}

    return Response(response_msg, status=status.HTTP_200_OK)