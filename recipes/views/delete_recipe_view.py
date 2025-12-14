from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from recipes.helpers import log_action
from recipes.models import Recipe, AdminLog

def check_admin(user):
    return user.is_superuser

@login_required
def delete_recipe(request, recipe_id):
    # Standard user delete 
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user == recipe.author:
        # Log the action before deletion
        log_action(
            actor=request.user,
            action_type=AdminLog.ActionType.RECIPE_DELETED,
            description=f"{request.user.username} deleted recipe '{recipe.name}' (ID: {recipe.id})",
            target_type='Recipe',
            target_id=recipe.id,
            metadata={
                'recipe_name': recipe.name,
                'recipe_author': recipe.author.username,
            },
            request=request,
        )
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
    
    # Log the action before deletion
    log_action(
        actor=request.user,
        action_type=AdminLog.ActionType.RECIPE_DELETED,
        description=f"{request.user.username} (Admin) deleted recipe '{recipe.name}' (ID: {recipe.id})",
        target_type='Recipe',
        target_id=recipe.id,
        metadata={
            'recipe_name': recipe.name,
            'recipe_author': recipe.author.username,
            'deleted_by_admin': True,
        },
        request=request,
    )
    
    recipe.delete()
    messages.success(request, "Recipe successfully deleted by Admin.")
    return redirect('dashboard')