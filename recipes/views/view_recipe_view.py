from django.shortcuts import get_object_or_404, render
from recipes.models import (
    Recipe,
    RecipeIngredient, 
    RecipeStep, 
    RecipeRating
)

def view_recipe(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.select_related("author").prefetch_related("tags"),
        pk=recipe_id
    )

    ingredients = RecipeIngredient.objects.filter(recipe=recipe).order_by("position")
    steps = RecipeStep.objects.filter(recipe=recipe).order_by("position")
    ratings = RecipeRating.objects.select_related("user").filter(recipe=recipe).order_by("-createdAt")

    return render(request, "view_recipe.html", {
        "recipe": recipe,
        "ingredients": ingredients,
        "steps": steps,
        "ratings": ratings,
    })
