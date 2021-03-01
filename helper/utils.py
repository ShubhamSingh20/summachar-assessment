from django.contrib.auth import get_user_model

User = get_user_model()

class TestEssentials(object):
    
    def create_user(self, username, email= None, password ='password') -> User:
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        return user

    def jwt_login(self) -> User:
        user = self.create_user('dev', 'dev@admin.com', 'admin')
        self.client.post('/api/v1/auth/login/', {
            'usernamel' : 'dev',
            'password': 'admin'
        }, format='json')

        return user