from django.db.models import base
from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from quiz import views

router = DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router.register(r'quizzes', views.QuizViewSet, basename='quizzes')

urlpatterns = [
    path('', include(router.urls)),
]
