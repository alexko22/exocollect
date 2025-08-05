from django.contrib import admin

# Register your models here.
from .models import Profiles
admin.site.register(Profiles)

from .models import Planet
admin.site.register(Planet)
