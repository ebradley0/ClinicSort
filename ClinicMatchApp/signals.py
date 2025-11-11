from django.contrib.auth.signals import user_logged_in

from django.dispatch import receiver
from django.core.signals import request_started
from .models import Student, Professor
from social_django.models import UserSocialAuth
from django.core.exceptions import ObjectDoesNotExist
from dotenv import load_dotenv
import os


load_dotenv()









def userAuthenticated_handler(sender, request, user, **kwargs):
    if not user.email: #If the user is manually created then skip this process, this is mostly used for dev and won't be in production
        print("User has no email associated, cannot create Student object.")
        return
    
    # This is to allow admin panel access. Contact IRT to figure out a better way to do this later.
    try:
        UserAuthObject = UserSocialAuth.objects.get(user=user)
    except ObjectDoesNotExist:
        print(f"No UserSocialAuth found for {user.username} — probably a local/admin login. Skipping student sync.")
        return
    


    
    
    

user_logged_in.connect(userAuthenticated_handler) # using @receiver was failing for an unknown reason

