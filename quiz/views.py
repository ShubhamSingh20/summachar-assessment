from quiz.models import Quiz, Question
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from quiz.serializers import QuizSerializer, QuestionSerializer

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
