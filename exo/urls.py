# imports
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

# url patterns
urlpatterns = [
    path('signup/', views.CreateProfileView.as_view(), name="signup"),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('start/', views.start_game, name="exocollect_start"),
    path('profile/<int:pk>', views.ShowProfileView.as_view(), name="profile"),
    path('generate-planet/', views.generate_random_planet, name='generate_planet'),
    path('planet/<int:pk>', PlanetView.as_view(), name="show_planet"),
]