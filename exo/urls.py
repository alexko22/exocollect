# imports
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

# url patterns
urlpatterns = [
    path('', ShowHome.as_view(), name="home"),
]