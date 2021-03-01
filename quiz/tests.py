from helper.utils import TestEssentials
from quiz.models import Question, Quiz
from accounts.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

# Create your tests here.
class QuizTest(TestCase, TestEssentials):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = self.jwt_login()

    def test_quiz_create(self):
        pass

    def test_quiz_update(self):
        pass

class QuestionTest(TestCase, TestEssentials):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = self.jwt_login()

    def test_question_create(self):
        pass

    def test_question_update(self):
        pass
