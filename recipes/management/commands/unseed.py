from django.core.management.base import BaseCommand
from recipes.models import (
    User, Recipe, RecipeRating, RecipeFavourite, Tag, AdminLog
)

class Command(BaseCommand):
    help = "Removes seeded sample data from the database"

    def handle(self, *args, **options):
        AdminLog.objects.filter(metadata__seed=True).delete()

        RecipeRating.objects.all().delete()
        RecipeFavourite.objects.all().delete()
        Recipe.objects.all().delete()

        Tag.objects.all().delete()

        User.objects.filter(is_staff=False).delete()

        self.stdout.write(self.style.SUCCESS("Database unseeding complete!"))
