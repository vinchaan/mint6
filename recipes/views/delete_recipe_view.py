from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe

# --- Helper to allow mocking in tests ---
def check_admin(user):
    return user.is_superuser

@login_required
def delete_recipe(request, recipe_id):
    # Standard user delete 
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
        messages.success(request, "Recipe deleted.")
    else:
        messages.error(request, "Permission denied.")
    return redirect('dashboard')

@login_required
def delete_recipe_admin(request, recipe_id):
    # Check admin permission
    if not check_admin(request.user):
        messages.error(request, "Admin access required.")
        return redirect('dashboard')

    # Get and delete
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    
    messages.success(request, "Recipe successfully deleted by Admin.")
    return redirect('dashboard')