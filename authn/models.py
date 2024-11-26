import uuid

from django.contrib.auth.hashers import make_password
from django.db import models


# Create your models here.
class User(models.Model):
    _id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=128, default=None, blank=True, null=True, unique=True
    )
    password = models.CharField(
        max_length=128, default=None, blank=True, null=True, unique=False
    )
    e_mail = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,
        null=False,
        editable=True,
        default="default@default.com",
    )
    last_login = models.DateTimeField(default=None, blank=True, null=True, unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        user = User.objects.filter(_id=self._id).first()
        if user is None or self.password != user.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self._id}"
