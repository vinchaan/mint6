from django.conf import settings
from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
