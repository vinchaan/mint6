from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from recipes.models import Recipe

@login_required
def dashboard(request):
    """
    Display the current user's dashboard.
    """
    current_user = request.user
    
    # FIX: Changed '-created_at' to '-createdAt' to match your Model field
    recipes = Recipe.objects.filter(author=current_user).order_by('-createdAt')

    return render(request, 'dashboard.html', {
        'user': current_user,
        'recipes': recipes, 
    })
    
