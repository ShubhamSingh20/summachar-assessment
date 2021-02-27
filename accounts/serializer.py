from accounts.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.validators import UnicodeUsernameValidator

class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='slug')
    last_name = serializers.CharField()
    first_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(validators=[
        UnicodeUsernameValidator(),
        UniqueValidator(queryset=User.objects.all()),
    ])
    email = serializers.EmailField(validators=[
        UniqueValidator(queryset=User.objects.all())
    ])

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 
            'first_name', 'last_name', 'password'
        ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def create(self, validated_data) -> User:
        user : User = super().create(validated_data)
        if password := validated_data.get('password', False):
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data) -> User:
        user : User = super().update(instance, validated_data)
        if password := validated_data.get('password', False):
            user.set_password(password)
            user.save()
        return user
