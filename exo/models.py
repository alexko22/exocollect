from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.templatetags.static import static


# Create your models here.
class Profiles(models.Model):
    display_name = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        ''' returns string version of the model '''
        return f'{self.display_name}'
    
    def get_planets(self):
        ''' gets all the planets associated with the current user via profile '''
        planets = Planet.objects.filter(profile=self)
        return planets
    
class Planet(models.Model):
    designation = models.TextField(blank=True)
    mass = models.FloatField(blank=True)
    gravity = models.FloatField(blank=True)
    comp = models.JSONField(blank=True)
    p_type = models.TextField(blank=True)
    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name='planets')

    def __str__(self):
        ''' returns a string version of the model '''
        return f'{self.designation}'
    
    # incomplete
    @property
    def get_image(self):
        return static('images/planet_templates/blue_planet.png')
