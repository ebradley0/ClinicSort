from django.contrib.auth.signals import user_logged_in

from django.dispatch import receiver
from django.core.signals import request_started
from .models import Student, Professor
from social_django.models import UserSocialAuth








def userAuthenticated_handler(sender, request, user, **kwargs):
    print("USER LOGGED IN SIGNAL FIRED")
    print(user)
    if not user.email: #If the user is manually created then skip this process, this is mostly used for dev and won't be in production
        print("User has no email associated, cannot create Student object.")
        return
    UserAuthObject = UserSocialAuth.objects.get(user=user) # Get the Social auth object from social_django. This is made and managed automatically on login
    
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