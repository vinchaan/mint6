from django.conf import settings
from django.db import models
from .recipe_tag import Tag

class Recipe(models.Model):


    DIFFICULTY_CHOICES = [
        ("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")
    ]

    VISIBILITY_CHOICES = [
        ("public", "Public"), ("private", "Private"), ("unlisted", "Unlisted")
    ]


    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=False)


    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
    )

    serves = models.PositiveSmallIntegerField(blank=False)

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        blank=False,
    )

    prepTime = models.DurationField(blank=False)
    cookTime = models.DurationField(blank=False)
    totalTime = models.DurationField(null=False, blank=False, editable=False)

    

    cuisine = models.CharField(max_length=100, blank=True)
    visibility = models.CharField(
        max_length = 10,
        choices=VISIBILITY_CHOICES,
        blank=False
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        blank=True,
    )

    averageRating = models.DecimalField(max_digits=2, decimal_places=1, default = 0)
    ratingCount = models.PositiveSmallIntegerField(default = 0)
    favouritesCount = models.PositiveSmallIntegerField(default = 0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        prep = self.prepTime
        cook = self.cookTime
        self.totalTime = prep+cook
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
