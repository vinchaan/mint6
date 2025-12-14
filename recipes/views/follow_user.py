from django.shortcuts import redirect
from django.contrib.auth import get_user_model

def follow_user(request, pk):
    User = get_user_model()

    user_being_followed = User.objects.get(pk=pk)
    if request.user in user_being_followed.all(): #get the list of all being followed see if the user requesting it is in this list
        user_being_followed.followers.remove(request.user) # to find users irrespective of case sensitivity/with or without @
    else:
        user_being_followed.followers.add(request.user)

    return redirect('profile', pk=pk)