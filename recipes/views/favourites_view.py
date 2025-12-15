from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from recipes.models import RecipeFavourite


@login_required
def favourites(request):
    """
    Display the current user's favourite recipes.
    """
    favourites_qs = (
        RecipeFavourite.objects.filter(user=request.user)
        .select_related("recipe", "recipe__author")
        .prefetch_related("recipe__tags")
        .order_by("-savedAt")
    )
    recipes = [fav.recipe for fav in favourites_qs]

    return render(
        request,
        "favourites.html",
        {
            "recipes": recipes,
        },
    )

