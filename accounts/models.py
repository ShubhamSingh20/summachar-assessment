from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class User(AbstractUser):
    slug = models.UUIDField(default=uuid4, editable=False)

    def __str__(self):
        return '< %s >' % self.username
