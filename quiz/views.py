from typing import List

from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from helper.viewsets import ModelViewSetWithoutList
from helper.permissions import AdminUserOnly

from quiz.exceptions import QuizNotTakenException
from quiz.models import Question, Quiz, TakenQuiz
from quiz.permissions import IsQuizLive, IsQuizTaken
from quiz.serializers import (
    QuestionSerializer, QuizSerializer, 
    QuizWithoutQuestionsSerializer, 
    UserTakenQuizSolutionSerializer
)

# Create your views here.
class QuestionViewSet(ModelViewSetWithoutList):
    lookup_field = 'slug'
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self) -> List:
        permission_classes = []

        if self.action == 'retrieve':
            permission_classes = [IsQuizLive]

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [AdminUserOnly]

        return [permission() for permission in permission_classes]

class QuizViewSet(ModelViewSet):
    lookup_field = 'slug'
    queryset = Quiz.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self) -> Serializer:
        if self.action == 'list':
            """
            No need to list out all the questions for all the quiz,
            only return questions when a quiz pk is specified
            """
            return QuizWithoutQuestionsSerializer

        if self.action in ['retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return QuizSerializer

    def get_permissions(self) -> List:
        permission_classes = []

        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        
        if self.action == 'user_answers':
            permission_classes = [IsAuthenticated]

        if self.action == 'user_submit':
            permission_classes = [IsAuthenticated, IsQuizLive, IsQuizTaken]

        if self.action == 'retrieve':
            # a non admin user can only view the quiz 
            # questions when it's live
            permission_classes = [IsQuizLive] if not self.request.user.is_superuser else [IsAdminUser]

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [AdminUserOnly]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer) -> None:
        user = self.request.user
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer) -> None:
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def user_submit(self, request, slug) -> Response:
        answers = request.data.get('answers', False)

        if not answers:
            return Response(
                {'expected_field' : ['expected field `answers` not present']}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserTakenQuizSolutionSerializer(data=answers, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quiz : Quiz = self.get_object()
        taken_quiz = TakenQuiz.objects.create(quiz=quiz, user=self.request.user)
        serializer.save(taken_quiz=taken_quiz)
        taken_quiz.save_total_score()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def user_answers(self, request, slug) -> Response:
        quiz : Quiz = self.get_object()

        try:
            taken_quiz = TakenQuiz.objects.get(quiz=quiz, user=request.user)
        except TakenQuiz.DoesNotExist:
            raise QuizNotTakenException

        serializer = UserTakenQuizSolutionSerializer(instance=taken_quiz.answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
