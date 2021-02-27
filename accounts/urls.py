from accounts import views
from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/check/', views.JWTAuthMe.as_view(), name='token_verify'),
    path('auth/logout/', views.JWTLogout.as_view(), name='token_delete'),
    path('auth/login/', views.JWTAuthLogin.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', views.JWTAuthRefresh.as_view(), name='token_refresh'),
]
