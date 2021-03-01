from django.contrib.auth import get_user_model

User = get_user_model()

class TestEssentials(object):

    def jwt_login(self) -> User:
        user = User.objects.create_user(
            username='test_user', password='password'
        )
        res = self.client.post('/api/v1/auth/login/', {
            'username' : 'test_user',
            'password': 'password'
        }, format='json')

        return user

    def make_user_admin(self, func):
        user = func()
        user.is_superuser = True
        user.save()
        return user