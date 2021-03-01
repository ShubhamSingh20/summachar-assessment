from helper.utils import TestEssentials
from quiz.models import Question, Quiz, TakenQuiz
from accounts.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

# Create your tests here.
class QuizTest(TestCase, TestEssentials):

    def setUp(self) -> None:
        self.client = APIClient()

    @property
    def get_quiz_data(self) -> dict:
        return {
            'name': 'First Test Quiz',
            'schedule_date': '2020-02-23 11:15:23',
            'end_date': '2020-02-28 23:59:59',
            'description': 'This is the first quiz',
            'time_per_question': 10,
            'questions': [
                {
                    'question_text': 'First Question',
                    'question_type': 'mcq',
                    'answer': 'C',
                },
                {
                    'question_text': 'Second Question',
                    'question_type': 'open_text',
                    'answer': 'final',
                } 
            ]
        }

    def test_quiz_create(self) -> None:
        self.make_user_admin(self.jwt_login)

        response : Response = self.client.post(
            '/api/v1/quizzes/', self.get_quiz_data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.all().count(), 1)
        self.assertEqual(Question.objects.all().count(), 2)

    def test_quiz_update(self) -> None:
        self.make_user_admin(self.jwt_login)

        response : Response = self.client.post(
            '/api/v1/quizzes/', self.get_quiz_data, 
            format='json'
        )

        data = {    
            'questions': [
                {
                    'question_text': 'Third Question',
                    'question_type': 'mcq',
                    'answer': 'A',
                },
            ]
        }

        quiz_slug = response.data.get('id')
        response : Response = self.client.patch(
            '/api/v1/quizzes/%s/' % quiz_slug, data, 
            format='json'
        )

        quiz = Quiz.objects.get(slug=quiz_slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(quiz.questions.count(), 3)

class QuizTakenTest(TestCase, TestEssentials):

    def setUp(self) -> None:
        self.client = APIClient()

    @property
    def get_quiz_data(self) -> dict:
        return {
            'name': 'First Test Quiz',
            'schedule_date': '2020-02-23 11:15:23',
            'end_date': '2020-02-28 23:59:59',
            'description': 'This is the first quiz',
            'time_per_question': 10,
            'questions': [
                {
                    'question_text': 'First Question',
                    'question_type': 'mcq',
                    'answer': 'C',
                },
                {
                    'question_text': 'Second Question',
                    'question_type': 'open_text',
                    'answer': 'final',
                } 
            ]
        }

    def test_take_quiz(self) -> None:
        user = self.make_user_admin(self.jwt_login)

        # create a quiz with questions
        response = self.client.post(
            '/api/v1/quizzes/', self.get_quiz_data, 
            format='json'
        )

        quiz_slug = response.data.get('id')
        quiz = Quiz.objects.get(slug=quiz_slug)

        data = {
            'answers': [
                {
                    'question': Question.objects.filter(question_text__startswith='First').first().slug,
                    'answer': 'b' # incorrect answer !
                },
                {
                    'question': Question.objects.filter(question_text__startswith='Second').first().slug,
                    'answer': 'final' # correct
                }
            ] 
        }

        response : Response = self.client.post(
            '/api/v1/quizzes/%s/user_submit/' % quiz_slug, 
            data, format='json'
        )
        taken_quiz = TakenQuiz.objects.get(user=user, quiz=quiz)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(taken_quiz.score, 1) # since one answer is incorrect

