from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from recipes.models import (
    RecipeFavourite,
    RecipeRating
)


@receiver([post_save, post_delete], sender=RecipeRating)
def update_recipe_rating_stats(sender, instance, **kwargs):
    """Update recipe stats when a rating is added/changed/deleted."""
    instance.recipe.update_rating_stats()


@receiver([post_save, post_delete], sender=RecipeFavourite)
def update_recipe_favourite_count(sender, instance, **kwargs):
    """Update recipe favourite count when a favourite is added/deleted."""
    instance.recipe.update_favourite_count()