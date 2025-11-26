from django.db import models


class RecipeStep(models.Model):
    
    recipe = models.ForeignKey(
        "Recipe",
        on_delete = models.CASCADE,
        related_name = "steps"
    )

    text = models.TextField()
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ["position"]
    
    def __str__(self):
        return f"Step {self.position} for {self.recipe}"