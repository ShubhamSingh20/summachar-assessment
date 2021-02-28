from quiz.models import Quiz, TakenQuiz
from rest_framework.permissions import BasePermission

class HaveRole(BasePermission):
    message = 'User Does not have required role to perform this action.'

    def has_permission(self, request, view):
        return request.user.role == view.required_role

class QuizIsLive(BasePermission):
    message = 'User Does not have required role to perform this action.'

    def has_permission(self, request, view):
        return request.user.role == view.required_role

class IsQuizTaken(BasePermission):
    message = 'User Has already taken this quiz, cannot retake it.'

    def has_object_permission(self, request, view, quiz : Quiz):
        return not TakenQuiz.objects.filter(user=request.user, quiz=quiz).exists()

class IsQuizLive(BasePermission):
    message = 'Quiz is not live.'

    def has_object_permission(self, request, view, quiz : Quiz):
        return quiz.is_live

