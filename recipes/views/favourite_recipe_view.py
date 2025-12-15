# recipes/views/favourite_recipe_view.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from recipes.models import Recipe, RecipeFavourite


@login_required
def favourite_recipe(request, recipe_id):
    """
    Toggle favourite status for a recipe.
    """
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user = request.user
    
    # Check if already favourited
    favourite, created = RecipeFavourite.objects.get_or_create(
        recipe=recipe,
        user=user
    )
    
    if not created:
        # Already favourited, so remove it
        favourite.delete()
        messages.success(request, f'Removed "{recipe.name}" from your favourites.')
    else:
        # Just created, so it's now favourited
        messages.success(request, f'Added "{recipe.name}" to your favourites.')
    
    return redirect('view_recipe', recipe_id=recipe_id)


