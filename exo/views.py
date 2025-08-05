# Create your views here.
# import statements
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import *
from django.urls import reverse
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
# from django.contrib.auth import login
# from .forms import *
# from plotly (for team type graphing)
# import plotly
# import plotly.graph_objs as go

# Class to show the home page
class ShowHome(TemplateView):
    ''' class to connect home URL to correct HTML template '''
    template_name = "exo/show_home.html"

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'exo/signup.html', {"form": form})

def start_game(request):
    return render(request, 'exo/start_game.html')

@login_required
def profile(request):
    return render(request, 'exo/profile.html', {'user': request.user})
