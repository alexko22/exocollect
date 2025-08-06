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

COMPOSITIONS = ["Gas Giant", "Rocky", "Icy", "Oceanic", "Carbon"]

@login_required
def generate_random_planet(request):
    profile = get_object_or_404(Profiles, user=request.user)

    name = f"Planet-{random.randint(1000, 9999)}"
    mass = round(random.uniform(0.1, 10.0), 2)
    gravity = round(random.uniform(3.0, 25.0), 1)
    comp = random.choice(COMPOSITIONS)

    planet = Planet.objects.create(
        profile=profile,
        designation=name,
        mass=mass,
        gravity=gravity,
        comp=comp,
    )

    return redirect('show_planet', pk=planet.pk)