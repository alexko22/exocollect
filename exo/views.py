# Create your views here.
# import statements
import random
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import *
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import *
from django.contrib.auth.views import LoginView

# from plotly (for team type graphing)
# import plotly
# import plotly.graph_objs as go

# Class to show the home page
class ShowHome(TemplateView):
    ''' class to connect home URL to correct HTML template '''
    template_name = "exo/show_home.html"

class CreateProfileView(View):
    ''' class to handle user and profile creation '''
    def get(self, request):
        user_form = UserCreationForm()
        profile_form = CreateProfilesForm()
        return render(request, "exo/signup.html", {
            "user_form": user_form,
            "profile_form": profile_form
        })

    def post(self, request):
        user_form = UserCreationForm(request.POST)
        profile_form = CreateProfilesForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            login(request, user)  # Log in the new user
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect(reverse("profile", kwargs={"pk": profile.pk}))

        return render(request, "exo/signup.html", {
            "user_form": user_form,
            "profile_form": profile_form
        })
    
class CustomLoginView(LoginView):
    template_name = 'exo/login.html'

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': Profiles.objects.get(user=self.request.user).pk
})

class ShowProfileView(DetailView, LoginRequiredMixin):
    ''' show the current users profile '''
    model = Profiles
    template_name = "exo/profile.html"
    context_object_name = "profile"

class PlanetView(DetailView):
    ''' class to view an individual planet screen '''
    model = Planet
    template_name = "exo/show_planet.html"
    context_object_name = "planet"

# def signup(request):
    # if request.method == "POST":
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
            # form.save()
            # return redirect('login')
    # else:
        # form = UserCreationForm()
    # return render(request, 'exo/signup.html', {"form": form})

def start_game(request):
    return render(request, 'exo/start_game.html')

# @login_required
# def profile(request):
    # return render(request, 'exo/profile.html', {'user': request.user})

COMPOSITIONS = ["Nitrogen", "Oxygen", "Carbon Dioxide", "Hydrogen", "Helium", "Argon", "Methane", "Neon", "Sulfur Dioxide", "Carbon Monoxide", "None"]

P_TYPES = ["Terrestrial", "Gas Giant", "Ice Giant", "Ocean Planet", "Mini-Neptune", "Dyson-Sphere"]
P_TYPE_PROB = [0.35, 0.25, 0.18, 0.1, 0.1, 0.02]

ATMOS_PROBS = {
  "Terrestrial": [0.60,0.15,0.03,0.01,0.01,0.03,0.01,0.01,0.01,0.01,0.12],
  "Gas Giant":  [0.01,0.01,0.01,0.38,0.40,0.01,0.10,0.02,0.01,0.01,0.04],
  "Ice Giant":  [0.01,0.01,0.01,0.12,0.56,0.01,0.20,0.05,0.01,0.01,0.01],
  "Ocean Planet":[0.40,0.25,0.15,0.01,0.01,0.05,0.01,0.01,0.05,0.05,0.01],
  "Mini-Neptune":[0.02,0.01,0.01,0.28,0.50,0.01,0.12,0.01,0.01,0.01,0.02],
  "Dyson-Sphere":[0,0,0,0,0,0,0,0,0,0,1.0]
}

MASS_RANGES = {
    "Terrestrial": (0.1, 3.0),    
    "Gas Giant": (50.0, 300.0), 
    "Ice Giant": (10.0, 50.0),
    "Ocean Planet": (0.5, 3.0),    
    "Mini-Neptune": (2.0, 10.0),   
    "Dyson-Sphere": (1000.0, 5000.0), }

RADIUS_RANGES = {
    "Terrestrial": (0.8, 1.5),
    "Gas Giant": (8, 15),
    "Ice Giant": (3, 6),
    "Ocean Planet": (1, 2),
    "Mini-Neptune": (2, 4),
    "Dyson-Sphere": (1000, 5000), 
}

G_CONST = 9.8

NAME_PREFIXES = ["Astra", "Nova", "Vortex", "Zenith", "Orion", "Luna", "Eclipse", "Nebula", "Solara", "Galaxis"]


@login_required
def generate_random_planet(request):
    profile = get_object_or_404(Profiles, user=request.user)

    p_type = random.choices(P_TYPES, weights=P_TYPE_PROB, k=1)[0]
    comp = random.choices(COMPOSITIONS, weights=ATMOS_PROBS[p_type], k=3)
    mass_min, mass_max = MASS_RANGES[p_type]
    mass = round(random.uniform(mass_min, mass_max), 2)
    # helper for gravity calculation
    radius = random.uniform(*RADIUS_RANGES[p_type])
    gravity = round(G_CONST * (mass / (radius ** 2)), 2)
    name = f"{random.choice(NAME_PREFIXES)}-{random.randint(1000, 9999)}"
   

    planet = Planet.objects.create(
        profile=profile,
        designation=name,
        mass=mass,
        gravity=gravity,
        p_type = p_type,
        comp=comp,
    )

    return redirect('show_planet', pk=planet.pk)