from helper.models import User
from django.http import Http404
from rest_framework import status
from quiz.models import Quiz, Question, TakenQuiz
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from quiz.serializers import QuizSerializer, QuestionSerializer, UserTakenQuizSolutionSerializer

# Create your views here.

class QuestionViewSet(ModelViewSet):
    permissions = [IsAuthenticated]
    lookup_field = 'slug'
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def paginate_queryset(self, queryset):
        if 'all' not in self.request.GET:
            return super().paginate_queryset(queryset)

class QuizViewSet(ModelViewSet):
    permissions = [IsAuthenticated]
    lookup_field = 'slug'
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Quiz.objects.filter(created_by=self.request.user)

    def paginate_queryset(self, queryset):
        if 'all' not in self.request.GET:
            return super().paginate_queryset(queryset)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_quiz(self, pk):
        try:
            return Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            raise Http404

    @action(detail=True, methods=['post'])
    def user_submission(self, request, pk) -> User:
        quiz : Quiz = self.get_quiz(pk)
        serializer = UserTakenQuizSolutionSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        taken_quiz = TakenQuiz.objects.create(quiz=quiz, user=self.request.user)
        serializer.save(taken=taken_quiz)
        taken_quiz.save_total_score()
        return Response(serializer.data, status=status.HTTP_200_OK)

