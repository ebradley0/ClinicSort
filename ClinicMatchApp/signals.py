from django.contrib.auth.signals import user_logged_in

from django.dispatch import receiver
from django.core.signals import request_started
from .models import Student, Professor








def userAuthenticated_handler(sender, request, user, **kwargs):
    print("USER LOGGED IN SIGNAL FIRED")
    print(user)
    created, updated = Student.objects.get_or_create(first_name=user.first_name,
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