from typing import Any, Dict

from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,TokenRefreshSerializer)
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

from accounts.models import User
from accounts.serializer import UserSerializer

# Create your views here.

class LoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs) -> Dict:
        data : Dict = super().validate(attrs)
        data['user'] = UserSerializer(instance=self.user).data
        return data

class JWTAuthLogin(TokenObtainPairView):
    serializer_class = LoginObtainPairSerializer

    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)

        if accessToken := response.data['access']:
            response.set_cookie('jwt', accessToken, httponly=True)

        if refreshToken := response.data['refresh']:
            response.set_cookie('refresh', refreshToken, httponly=True)

        return response

class JWTAuthRefresh(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)

        if accessToken := response.data['access']:
            response.set_cookie('jwt', accessToken, httponly=True)

        if refreshToken := response.data['refresh']:
            response.set_cookie('refresh', refreshToken, httponly=True)

        return response

class JWTAuthMe(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        return Response({
            'user': UserSerializer(instance=request.user).data
        }, status=status.HTTP_200_OK)

class JWTLogout(APIView):
    """
        Need to implment a token blacklisting startegy later on
        to invalidate tokens
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        response = Response({
            'detail': 'logged out successfully',
        }, status=status.HTTP_200_OK)

        response.delete_cookie('jwt')
        response.delete_cookie('refresh')

        return response

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'slug'
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminUser]

    def paginate_queryset(self, queryset) -> Any:
        if 'all' not in self.request.GET:
            return super().paginate_queryset(queryset)
