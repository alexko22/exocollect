from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Profiles(models.Model):
    display_name = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        ''' returns string version of the model '''
        return f'{self.display_name}'
    
    def get_planets(self):
        ''' gets all the planets associated with the current user via profile '''
        planets = Planet.objects.filter(prof=self)
        return planets
    
class Planet(models.Model):
    designation = models.TextField(blank=True)
    mass = models.FloatField(blank=True)
    gravity = models.FloatField(blank=True)
    comp = models.JSONField(blank=True)
    prof = models.ForeignKey(Profiles, on_delete=models.CASCADE)

    def __str__(self):
        ''' returns a string version of the model '''
        return f'{self.designation}'
