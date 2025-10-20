from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@reciever(user_logged_in)
def userAuthenticated_handler(sender, request, user, **kwargs):
    print("USER LOGGED IN SIGNAL FIRED")
    print(user)