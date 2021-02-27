from django.test import TestCase
from rest_framework import serializers
from accounts.models import User
from collections import OrderedDict
from helper.validators import NestedDataUnqiueValidator
from rest_framework.test import APIClient
# Create your tests here.
class NestedDataUniqueValidatorTest(TestCase):

    def setUp(self) -> None:
        self.validator = NestedDataUnqiueValidator

    def test_with_non_unqiue_data(self):
        data = [
            OrderedDict([('id', '123'), ('name', 'first')]),
            OrderedDict([('id', '123')]),
        ]

        self.assertRaises(serializers.ValidationError, self.validator(), **{'value': data})
    
    def test_with_ignore_field(self):
        data = [
            OrderedDict([('id', '123'), ('name', 'first')]),
            OrderedDict([('id', '123')]),
        ]

        self.assertIsNone(self.validator(ignore=['id'])(**{'value': data}))

class S3SignedUrlTest(TestCase):
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
        self.user = self.jwt_login()

    def test_s3_presigned_url(self):
        data = {
            'files': [
                {
                    'filename': 'Counter-strike  Global Offensive 2019.10.06 - 12.46.30.02.DVR.mp4',
                    'is_public' : True,
                },
                {
                    'filename': 'Counter-strike  Global Offensive 2019.10.06 - 12.46.30.02.DVR.mp4',
                    'is_public' : True,
                },
            ]
        }
        response = self.client.post('/api/v1/aws/s3/signed-urls/', data, format='json')
        self.assertEqual(response.status_code, 200)
