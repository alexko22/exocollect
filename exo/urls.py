# imports
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

# url patterns
urlpatterns = [
    path('signup/', views.CreateProfileView.as_view(), name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name='exo/login.html'), name="login"),
    path('start/', views.start_game, name="exocollect_start"),
    path('profile/', views.profile, name="profile"),
]