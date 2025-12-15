# recipes/views/view_profile_view.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from recipes.models import Recipe, RecipeRating

User = get_user_model()


@login_required
def view_profile(request, user_id):
    """
    Display another user's profile with their recipes and reviews.
    """
    profile_user = get_object_or_404(User, pk=user_id)
    current_user = request.user
    
    # Get user's recipes
    recipes = Recipe.objects.filter(author=profile_user).order_by('-createdAt')
    
    # Get user's ratings/reviews on other recipes
    user_ratings = RecipeRating.objects.filter(
        user=profile_user
    ).select_related('recipe', 'recipe__author').order_by('-createdAt')
    
    context = {
        'profile_user': profile_user,
        'recipes': recipes,
        'user_ratings': user_ratings,
        'is_own_profile': (current_user.id == profile_user.id),
    }
    
    return render(request, 'view_profile.html', context)


