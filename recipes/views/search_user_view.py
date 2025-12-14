from django.shortcuts import render
from django.contrib.auth import get_user_model

def search_user(request):
    User = get_user_model()

    search_query = request.GET.get('query', '')
    if search_query:
        users = User.objects.filter(username__icontains=search_query) # to find users irrespective of case sensitivity/with or without @
    else:
        users = User.objects.all() # before searching display all the users

    return render(request, 'search_user.html', {
        'results': users,
        'search_query': search_query
    })