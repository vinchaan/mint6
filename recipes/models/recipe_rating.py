from django.db import models
from .recipe import Recipe
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class RecipeRating(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipe_ratings",
    )

    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta: 
        unique_together=("recipe", "user")

    
    def __str__(self):
        return f"{self.rating}★ on {self.recipe} by {self.user}"
