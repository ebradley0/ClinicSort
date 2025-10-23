from django.contrib.auth.signals import user_logged_in

from django.dispatch import receiver
from django.core.signals import request_started
from .models import Student, Professor
from social_django.models import UserSocialAuth
from django.core.exceptions import ObjectDoesNotExist









def userAuthenticated_handler(sender, request, user, **kwargs):
    print("USER LOGGED IN SIGNAL FIRED")
    print(user)
    if not user.email: #If the user is manually created then skip this process, this is mostly used for dev and won't be in production
        print("User has no email associated, cannot create Student object.")
        return
    
    # This is to allow admin panel access. Contact IRT to figure out a better way to do this later.
    try:
        UserAuthObject = UserSocialAuth.objects.get(user=user)
    except ObjectDoesNotExist:
        print(f"No UserSocialAuth found for {user.username} — probably a local/admin login. Skipping student sync.")
        return
    created, updated = Student.objects.get_or_create(userAuth=UserAuthObject, first_name=user.first_name,
                                                    last_name=user.last_name,
                                                    email=user.email)
    if created:
        print("Created new Student object for user:", user)
    else:
        print("Found existing Student object for user:", user)

user_logged_in.connect(userAuthenticated_handler) # using @receiver was failing for an unknown reason

@receiver(request_started)
def page_loaded_handler(sender, environ, **kwargs):
    print("🚀 PAGE LOAD SIGNAL FIRED")