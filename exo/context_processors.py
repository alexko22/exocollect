from .models import *  # use your actual model name

def profile_for_user(request):
    profile = None
    if request.user.is_authenticated:
        profile = Profiles.objects.filter(user=request.user).first()
    return {'pro': profile}