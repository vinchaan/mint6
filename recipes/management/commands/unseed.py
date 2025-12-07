from django.core.management.base import BaseCommand, CommandError
from recipes.models import User, Recipe, RecipeIngredient, RecipeStep, RecipeRating, RecipeFavourite, Tag

class Command(BaseCommand):
    """
    Management command to remove (unseed) data from the database.

    This command deletes all seeded data including recipes, ingredients, steps,
    and non-staff users. It is designed to complement the corresponding "seed"
    command, allowing developers to reset the database to a clean state without
    removing administrative users.

    Attributes:
        help (str): Short description displayed when running
            `python manage.py help unseed`.
    """
    
    help = 'Removes seeded sample data from the database'

    def handle(self, *args, **options):
        """
        Execute the unseeding process.

        Deletes ratings, favourites, recipes (which cascades to ingredients and steps),
        tags, and then non-staff users. Prints confirmation messages showing
        counts of deleted objects.

        """

        RecipeRating.objects.all().delete()
        RecipeFavourite.objects.all().delete()
        Recipe.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

        self.stdout.write(
            self.style.SUCCESS('Database unseeding complete!')
        )