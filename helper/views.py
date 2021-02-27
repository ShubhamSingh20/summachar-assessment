from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# create views and actions here

@api_view(['GET'])
def ping(request) -> Response:
    return Response(data={'message' : 'pong'}, status=status.HTTP_200_OK)
