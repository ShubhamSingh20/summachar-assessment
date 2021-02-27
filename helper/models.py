from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User = get_user_model()

# Create your models here.
class ModelStamps(models.Model):
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated_at'), auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_created_by",
        related_query_name="%(app_label)s_%(class)ss"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name="%(app_label)s_%(class)s_updated_by",
        related_query_name="%(app_label)s_%(class)ss"
    )

    class Meta:
        abstract = True
