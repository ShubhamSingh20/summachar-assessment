from quiz.models import Question, Quiz
from services.models import Video
from accounts.models import User
from django.test import TestCase
from topics.models import Topic
from rest_framework import status
from topics.factories import TopicFactory
from rest_framework.test import APIClient

# Create your tests here.

class QuizTest(TestCase):
    def get_quiz_data(self):
        self.topic_factories.create_batch(3)

        return {
            'name' : 'Quiz First Name',
            'difficulty' : 10,
            'excellent_remark': 10,
            'good_remark': 4,
            'average_remark' : 2,
            'poor_remark' : 1,
            'quiz_type' : 'Revision',
            'topics' : Topic.objects.all().values_list('slug', flat=True)
        }

    def create_quiz_with_url(self, quizData):
        return self.client.post(
            '/api/v1/quizzes/',
            quizData, format='json'
        )

    def create_user(self, email= None, password ='password') -> User:
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        return user

    def jwt_login(self) -> User:
        user = self.create_user('dev@admin.com', 'admin')
        self.client.post('/api/v1/auth/login/', {
            'email' : 'dev@admin.com',
            'password': 'admin'
        }, format='json')
        return user

    def setUp(self) -> None:
        self.client = APIClient()
        self.topic_factories = TopicFactory
        self.user = self.jwt_login()

    def test_quiz_create(self):
        quiz_data = self.get_quiz_data()
        quiz_data['questions'] = [
            {
                'question_img' : 'https://some-random-question.com/image/',
                'question_type' : 'Objective',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'correct_solution' : 'A',
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            },
            {
                'question_img' : 'https://some-random-question.com/image/',
                'question_type' : 'Numerical',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'correct_solution' : 'A',
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            }
        ]
        response = self.client.post('/api/v1/quizzes/', quiz_data, format='json')
        self.assertIs(response.status_code, status.HTTP_201_CREATED, response.json())

        quiz = Quiz.objects.get(slug=response.json()['id'])
        self.assertEqual(Quiz.objects.all().count(), 1)
        self.assertEqual(quiz.questions.count(), 2)

    def test_quiz_update(self):
        quiz_data = self.get_quiz_data()
        quiz_data['questions'] = [
            {
                'question_img' : 'https://some-random-question.com/image/',
                'question_type' : 'Objective',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'correct_solution' : 'A',
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            },
            {
                'question_img' : 'https://some-random-question.com/image/',
                'question_type' : 'Numerical',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'correct_solution' : 'A',
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            }
        ]

        response = self.client.post('/api/v1/quizzes/', quiz_data, format='json')
        self.assertIs(response.status_code, status.HTTP_201_CREATED, response.json())
        quiz_slug = response.json()['id']

        quiz_data['questions'] = [
            {
                # update these
                'id' : Question.objects.get(pk=1).slug,
                'question_img' : 'https://some-random-question.com/image/1',
                'question_type' : 'Objective',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'correct_solution' : 'A',
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            },
            {
                'id' : Question.objects.get(pk=2).slug,
                'question_img' : 'https://some-random-question.com/image/2',
                'question_type' : 'Numerical',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'correct_solution' : 'A',
                    'timestamps': [],
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            },
            # create this one
            {
                'question_img' : 'https://some-random-question.com/image/3',
                'question_type' : 'Numerical',
                'difficulty' : 23,
                'correct_marks': 4,
                'incorrect_marks': 1,
                'unattempted_marks': 0,
                'solution': {
                    'solution_img' : 'https://some-random-solution.com/image/',
                    'correct_solution' : 'A',
                    'video' : {
                        'video_uri': 'https://some-random-solution.com/video/',
                        'timestamps': [],
                    }
                }
            }
        ]

        response = self.client.put('/api/v1/quizzes/{}/'.format(quiz_slug), quiz_data, format='json')
        self.assertIs(response.status_code, status.HTTP_200_OK, response.json())
        quiz = Quiz.objects.get(slug=quiz_slug)
        self.assertEqual(quiz.questions.count(), 3)

class QuestionTest(TestCase):
    def get_quiz_data(self):
        self.topic_factories.create_batch(3)

        return {
            'name' : 'Quiz First Name',
            'difficulty' : 10,
            'excellent_remark': 10,
            'good_remark': 4,
            'average_remark' : 2,
            'poor_remark' : 1,
            'quiz_type' : 'Revision',
            'topics' : [{'id': slug} for slug in Topic.objects.all().values_list('slug', flat=True)]
        }

    def create_quiz_with_url(self, quizData):
        return self.client.post(
            '/api/v1/quizzes/',
            quizData, format='json'
        )

    def create_user(self, email= None, password ='password') -> User:
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        return user

    def jwt_login(self) -> User:
        user = self.create_user('dev@admin.com', 'admin')
        self.client.post('/api/v1/auth/login/', {
            'email' : 'dev@admin.com',
            'password': 'admin'
        }, format='json')
        return user

    def setUp(self) -> None:
        self.client = APIClient()
        self.topic_factories = TopicFactory
        self.user = self.jwt_login()

    def test_question_create(self):
        quiz_data = self.get_quiz_data()
        topics = quiz_data.pop('topics')
        quiz = Quiz.objects.create(**quiz_data, **{'created_by': self.user, 'updated_by': self.user})
        quiz.topics.add(*[1,2,3])

        question_data = {
            'quiz': quiz.slug,
            'question_img' : 'https://some-random-question.com/image/1',
            'question_type' : 'Objective',
            'difficulty' : 23,
            'correct_marks': 4,
            'incorrect_marks': 1,
            'unattempted_marks': 0,
            'solution': {
                'solution_img' : 'https://some-random-solution.com/image/',
                'correct_solution' : 'A',
                'video': {
                    'video_uri' : 'https://some-random-solution.com/video/343434',
                    'timestamps': [
                        {
                            'timestamp': '12:43',
                            'label': 'UPDATED STAMP',
                        },
                        {
                            'timestamp': '13:34',
                            'label': 'UPDATED STAMP',
                        },
                    ]
                }
            }
        }

        response = self.client.post('/api/v1/questions/', question_data, format='json')
        self.assertIs(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(quiz.questions.count(), 1)

    def test_question_update(self):
        quiz_data = self.get_quiz_data()
        topics = quiz_data.pop('topics')
        quiz = Quiz.objects.create(**quiz_data, **{'created_by': self.user, 'updated_by': self.user})
        quiz.topics.add(*[1,2,3])

        question_data = {
            'quiz': quiz.slug,
            'question_img' : 'https://some-random-question.com/image/1',
            'question_type' : 'Objective',
            'difficulty' : 23,
            'correct_marks': 4,
            'incorrect_marks': 1,
            'unattempted_marks': 0,
            'solution': {
                'solution_img' : 'https://some-random-solution.com/image/',
                'correct_solution' : 'A',
                'video': {
                    'video_uri' : 'https://some-random-solution.com/video/343434',
                    'timestamps': [
                        {
                            'timestamp': '12:43',
                            'label': 'FIRST STAMP',
                        },
                        {
                            'timestamp': '13:34',
                            'label': 'SECOND STAMP',
                        },
                    ]
                }
            }
        }

        response = self.client.post('/api/v1/questions/', question_data, format='json')
        self.assertIs(response.status_code, status.HTTP_201_CREATED, response.json())
        question = Question.objects.get(slug=response.json()['id'])

        updated_question_data = {
            'question_img' : 'https://some-random-question.com/image/1',
            'question_type' : 'Objective',
            'difficulty' : 23,
            'correct_marks': 4,
            'incorrect_marks': 1,
            'unattempted_marks': 0,
            'solution': {
                'solution_img' : 'https://some-random-solution.com/image/',
                'correct_solution' : 'A',
                'video': {
                    # this should create a new video instance , since video uri has changed
                    'video_uri' : 'https://some-random-solution.com/video/changed-name',
                    'timestamps': [
                        {
                            'timestamp': '12:43',
                            'label': 'UPDATED STAMP',
                        },
                        {
                            'timestamp': '13:34',
                            'label': 'UPDATED STAMP',
                        },
                    ]
                }
            }
        }

        response = self.client.put('/api/v1/questions/%s/' % question.slug, updated_question_data, format='json')
        self.assertIs(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(quiz.questions.count(), 1)

        # since we changed the video uri we will have a new instance of video
        self.assertEqual(Video.objects.all().count(), 2)
        self.assertEqual(Video.objects.filter(deleted=True).count(), 1)

        question.refresh_from_db()
        self.assertIs(question.solution.solution_video.deleted, False)
        self.assertEqual(question.solution.solution_video.timestamps.count(), 2)

