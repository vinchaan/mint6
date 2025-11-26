from django.db import models


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        "Recipe",
        on_delete = models.CASCADE,
        related_name = "ingredients"
    )
    text = models.CharField(max_length = 255)
    position = models.PositiveIntegerField()
    
    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.text} ({self.recipe})"