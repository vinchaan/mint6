# recipes/views/add_rating_view.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from recipes.models import Recipe, RecipeRating
from recipes.forms import RecipeRatingForm


@login_required
def add_rating(request, recipe_id):
    """
    Add or update a rating and review for a recipe.
    """
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user = request.user
    
    # Try to get existing rating
    try:
        rating = RecipeRating.objects.get(recipe=recipe, user=user)
        is_new = False
    except RecipeRating.DoesNotExist:
        rating = None
        is_new = True
    
    if request.method == 'POST':
        form = RecipeRatingForm(request.POST, instance=rating)
        if form.is_valid():
            saved_rating = form.save(commit=False)
            saved_rating.recipe = recipe
            saved_rating.user = user
            saved_rating.save()
            if is_new:
                messages.success(request, 'Your rating has been added!')
            else:
                messages.success(request, 'Your rating has been updated!')
            return redirect('view_recipe', recipe_id=recipe_id)
    else:
        form = RecipeRatingForm(instance=rating)
    
    return render(request, 'add_rating.html', {
        'form': form,
        'recipe': recipe,
        'user_rating': rating,
    })

