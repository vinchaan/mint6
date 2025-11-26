from django.db import models
from .recipe import Recipe
from django.conf import settings


class RecipeFavourite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favourites",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favourite_recipes",
    )

    savedAt = models.DateTimeField(auto_now_add=True)

    class Meta: 
        unique_together=("recipe", "user")

    def __str__(self):
        return f"{self.user} likes {self.recipe}"