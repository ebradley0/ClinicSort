from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import HttpResponseForbidden #Blocking access if needed

def professor_only(func):
    @wraps(func) #Creating a wrapper for the function
    @login_required #Use thje login_requried check alongside the custom wrapper
    def wrapper(request, *args, **kwargs):
        socialAuth = request.user.social_auth.first() #Get their login object. This only exists if login_required passes, so we can use .first() without errors
        if socialAuth and hasattr(socialAuth, "professor"): #Lowercase because Django stores it internally with p, not P
            return func(request, *args, **kwargs) #Render the function if theyre a professor
        return HttpResponseForbidden("Access Restricted. Contact Admin if you believe this is incorrect.") #Otherwise block access
    return wrapper