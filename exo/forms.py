# forms.py

from django import forms
from .models import Profiles
# from .models import Profiles

# class: Create
class CreateProfilesForm(forms.ModelForm):
    ''' form to create a new profile '''
    class Meta:
        ''' associating form to profile model '''
        model = Profiles
        # which fields we want to display
        fields = ['display_name', 'bio']


class UpdateProfileForm(forms.ModelForm):
    ''' form to update a profile object '''
    class Meta:
        ''' associting form to Profile model '''
        model = Profiles
        # fields to be displayed
        fields = ['display_name', 'bio', 'pfp']