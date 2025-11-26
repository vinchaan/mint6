from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from recipes.helpers import can_delete_recipe
from recipes.models import Recipe


@login_required
def delete_recipe(request, recipe_id):
    """
    Delete a recipe (admin and moderator only).
    
    This view allows admins and moderators to delete any recipe.
    Regular users are redirected with an error message.
    """
    
    # Checks if user has permission to delete recipes
    if not can_delete_recipe(request.user):
        messages.error(request, "You do not have permission to delete recipes.")
        return redirect('dashboard')
    
    # Gets the recipe object
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    # TODO: Any additional checks here if needed
    # (e.g., check if recipe is in use, confirmation step, etc.)
    
    # TODO: Uncomment when ready to actually delete:
    # recipe.delete()
    # messages.success(request, f"Recipe '{recipe.name}' has been deleted.")
    
    # For now, just redirect (skeleton code)
    messages.info(request, f"Recipe deletion for '{recipe.name}' would happen here.")
    return redirect('dashboard')
    
    # TODO: Redirecting to a specific page (e.g., recipe list)
    # return redirect(reverse('recipe_list'))  # if we have a recipe list view

