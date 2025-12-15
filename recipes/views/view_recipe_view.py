from django.shortcuts import get_object_or_404, render
from recipes.models import (
    Recipe,
    RecipeIngredient, 
    RecipeStep, 
    RecipeRating,
    RecipeFavourite
)

def view_recipe(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.select_related("author").prefetch_related("tags"),
        pk=recipe_id
    )

    ingredients = RecipeIngredient.objects.filter(recipe=recipe).order_by("position")
    steps = RecipeStep.objects.filter(recipe=recipe).order_by("position")
    ratings = RecipeRating.objects.select_related("user").filter(recipe=recipe).order_by("-createdAt")
    
    # Check if user has favourited this recipe
    is_favourited = False
    user_rating = None
    if request.user.is_authenticated:
        is_favourited = RecipeFavourite.objects.filter(recipe=recipe, user=request.user).exists()
        try:
            user_rating = RecipeRating.objects.get(recipe=recipe, user=request.user)
        except RecipeRating.DoesNotExist:
            pass

    return render(request, "view_recipe.html", {
        "recipe": recipe,
        "ingredients": ingredients,
        "steps": steps,
        "ratings": ratings,
        "is_favourited": is_favourited,
        "user_rating": user_rating,
    })
