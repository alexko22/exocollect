from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Profiles(models.Model):
    username = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        ''' returns string version of the model '''
        return f'{self.username}'