from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.templatetags.static import static
import random


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
    
    # incomplete:
    @property
    def get_image(self):
        comp = self.comp or []

        # Map gas to base planet color
        gas_color_map = {
            'Methane': 'Blue',
            'Hydrogen': 'Red-ish',
            'Helium': 'Yellow',
            'Oxygen': 'Green',
            'Sulfur': 'Yellow',
            'Carbon Dioxide': 'Gray',
            'Water': 'Blue',
        }

        # Get all unique colors based on gas composition
        colors = []
        for gas in comp:
            color = gas_color_map.get(gas)
            if color and color not in colors:
                colors.append(color)

        # If no colors found, fallback based on type
        if not colors:
            if "Gas" in self.p_type:
                colors.append("Red-ish")
            elif "Ice" in self.p_type:
                colors.append("Purple")
            elif "Ocean" in self.p_type:
                colors.append("Blue")
            elif "Neptune" in self.p_type:
                colors.append("Blue-ish")
            else:
                colors.append("Green")

        # Build a set of available images
        available_images = [
            "Blue-ish Green Planet.png", "Blue-ish Purple Planet.png",
            "Blue-ish Red Planet.png", "Blue-ish Yellow Planet.png",
            "Green Planet.png", "Green-ish Brown Planet.png", "Green-ish Orange Planet.png",
            "Green-ish Pink Planet.png", "Purple Planet.png", "Purple-ish Blue Planet.png",
            "Purple-ish Gray Planet.png", "Purple-ish Green Planet.png",
            "Purple-ish Orange Planet.png", "Red Planet.png", "Red-ish Aqua Planet.png",
            "Red-ish Green Planet.png", "Red-ish Orange Planet.png", "Red-ish Violet Planet.png",
            "Yellow Planet.png", "Yellow-ish Gray Planet.png", "Yellow-ish Green Planet.png",
            "Yellow-ish Orange Planet.png", "Yellow-ish Violet Planet.png"
        ]

        # Try to find an image that contains all the relevant colors
        matching_images = [
            img for img in available_images
            if all(color in img for color in colors)
        ]

        # Fallback: allow partial matches (any color match)
        if not matching_images:
            matching_images = [
                img for img in available_images
                if any(color in img for color in colors)
            ]

        # Final fallback
        chosen_image = matching_images[0] if matching_images else "default_planet.png"

        return static(f'images/planet_templates/{chosen_image}')
