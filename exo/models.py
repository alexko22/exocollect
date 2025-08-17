from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.templatetags.static import static
import random


# Create your models here.
class Profiles(models.Model):
    PLANET_CHOICES = [
        ('Red Planet', 'Red Planet'),
        ('Purple Planet', 'Purple Planet'),
        ('Green Planet', 'Green Planet'),
    ]

    display_name = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    # new change
    pfp = models.TextField(choices=PLANET_CHOICES, default="Red Planet")

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
    
    # this is a work in progress
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

        if self.p_type == "Dyson-Sphere":
            if self.mass < 2500.0:
                return static('images/dyson_sphere_templates/normal_dyson_sphere.png')
            elif self.mass > 4000.0:
                return static('images/dyson_sphere_templates/green_dyson_sphere.png')
            else:
                return static('images/dyson_sphere_templates/red_dyson_sphere.png')
        else:

            return static(f'images/planet_templates/{chosen_image}')

        return static(f'images/planet_templates/{chosen_image}')
    
    def joined_gasses(self):
        if not self.comp:
            return ''
        # If comp is a list of strings
        filtered = [gas for gas in self.comp if gas and gas.lower() != 'none']
        return ', '.join(filtered)
    
    def earth_like(self):
        ''' returns a percentage score of how similar a plaent is to earth '''
        score = 0
        if self.p_type == "Terrestrial":
            score += 30
        elif self.p_type == "Ocean Planet":
            score += 20
        else:
            score += 5
        
        if "Argon" in self.comp:
            score += 10
        if "Nitrogen" in self.comp:
            score += 20
        if "Oxygen" in self.comp:
            score += 20
        if "Carbon Dioxide" in self.comp:
            score += 5
   
        mass_diff = abs(self.mass - 1)
        if mass_diff < 0.1:
            score += 10
        elif mass_diff < 0.5:
            score += 8
        elif mass_diff < 1.0:
            score += 6
        elif mass_diff < 2.0:
            score += 4
        else:
            score += 2

        gravity_diff = abs(self.gravity - 1)
        if gravity_diff < 0.1:
            score += 10
        elif gravity_diff < 0.5:
            score += 8
        elif gravity_diff < 1.0:
            score += 6
        elif gravity_diff < 2.0:
            score += 4
        else:
            score += 2

        return score

class Deck(models.Model):
    ''' model for exoclash game '''
    name = models.TextField(blank=True)
    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name='deck_prof', null=True, blank=True)
    p1 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p1')
    p2 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p2')
    p3 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p3')
    p4 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p4')
    p5 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p5')
    p6 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p6')
    p7 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p7')
    p8 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p8')
    p9 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p9')
    p10 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p10')
    p11 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p11')
    p12 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p12')
    p13 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p13')
    p14 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p14')
    p15 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p15')
    p16 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p16')
    p17 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p17')
    p18 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p18')
    p19 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p19')
    p20 = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='p20')

    # will define some helper methods here later...
 



        


