"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""

from faker import Faker
from faker_food import FoodProvider
from random import randint, random, choice, sample
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from recipes.models import (
    Recipe,
    RecipeIngredient,
    RecipeStep,
    RecipeRating,
    RecipeFavourite,
    Tag,
    User,
)


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

recipe_fixtures = [
    {
        'name': 'Weeknight Veggie Pasta',
        'author': '@johndoe',
        'description': 'A quick pasta tossed with colourful vegetables and a light garlic sauce.',
        'serves': 4,
        'difficulty': 'easy',
        'prep_minutes': 15,
        'cook_minutes': 20,
        'cuisine': 'Italian',
        'visibility': 'public',
        'tags': ['Quick', 'Family'],
        'ingredients': [
            '200g dried pasta',
            '1 courgette, sliced',
            '1 bell pepper, chopped',
            '2 cloves garlic, minced',
            '2 tbsp olive oil',
        ],
        'steps': [
            'Boil pasta in salted water until al dente.',
            'Sauté vegetables and garlic in olive oil until tender, then toss with pasta.',
        ],
    },
    {
        'name': 'Slow Sunday Roast',
        'author': '@janedoe',
        'description': 'Classic roast with hearty vegetables and rich gravy.',
        'serves': 6,
        'difficulty': 'medium',
        'prep_minutes': 25,
        'cook_minutes': 120,
        'cuisine': 'British',
        'visibility': 'public',
        'tags': ['Family', 'Comfort'],
        'ingredients': [
            '1.5kg beef joint',
            '4 carrots, chopped',
            '2 onions, quartered',
            '3 potatoes, halved',
            '500ml beef stock',
        ],
        'steps': [
            'Season and sear the beef, then roast with vegetables.',
            'Simmer beef stock with pan drippings to make gravy.',
        ],
    },
    {
        'name': 'Citrus Overnight Oats',
        'author': '@charlie',
        'description': 'Creamy oats brightened with fresh citrus for an easy breakfast.',
        'serves': 2,
        'difficulty': 'easy',
        'prep_minutes': 10,
        'cook_minutes': 0,
        'cuisine': 'American',
        'visibility': 'unlisted',
        'tags': ['Quick', 'Budget'],
        'ingredients': [
            '120g rolled oats',
            '250ml milk',
            '1 orange, zested and segmented',
            '1 tbsp honey',
            'Pinch of cinnamon',
        ],
        'steps': [
            'Stir oats, milk, honey, and cinnamon together.',
            'Fold in orange zest and segments, then chill overnight.',
        ],
    },
]

# Common recipe tags to seed
tag_fixtures = [
    'Quick',
    'Family',
    'Comfort',
    'Budget',
    'Vegetarian',
    'Vegan',
    'Gluten-Free',
    'Dairy-Free',
    'Spicy',
    'Healthy',
    'Meal Prep',
    'One-Pot',
    'Baking',
    'Dessert',
    'Breakfast',
]


class Command(BaseCommand):
    """
    Build automation command to seed the database with data.

    This command inserts a small set of known users (``user_fixtures``) and then
    repeatedly generates additional random users until ``USER_COUNT`` total users
    exist in the database. Each generated user receives the same default password.

    Attributes:
        USER_COUNT (int): Target total number of users in the database.
        DEFAULT_PASSWORD (str): Default password assigned to all created users.
        help (str): Short description shown in ``manage.py help``.
        faker (Faker): Locale-specific Faker instance used for random data.
    """

    USER_COUNT = 200
    RECIPE_COUNT = 50
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        """Initialize the command with a locale-specific Faker instance."""
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')
        self.faker.add_provider(FoodProvider)

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        First creates admin and moderator users. Then creates tags, users, recipes, ratings and favourites.
        """
        

        self.stdout.write("Starting database seeding...")
        self.create_staff()
        self.create_tags()
        self.create_users()
        self.create_recipes()
        self.create_ratings_and_favourites()
        self.users = User.objects.all()
        self.recipes = Recipe.objects.all()
        self.stdout.write(self.style.SUCCESS(f"Seeding complete! {self.users.count()} users, {self.recipes.count()} recipes, {Tag.objects.count()} tags"))

    def create_staff(self):
        try: 
            self.admin_user = User.objects.create_user(
                username='@admin',            
                email='admin@test.com',
                password='Password123',
                role=User.Roles.ADMIN,
            )

            self.moderator_user = User.objects.create_user(
                username='@moderator',
                email='moderator@test.com',
                password='Password123',
                role=User.Roles.MODERATOR,
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Did not generate admin and moderator due to already being generated."))


    def create_users(self):
        """
        Create fixture users and then generate random users up to USER_COUNT.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on username/email) are ignored and generation continues.
        """
        self.generate_user_fixtures()
        self.generate_random_users()

    def create_tags(self):
        """Create fixture tags to be used by recipes."""
        self.stdout.write("Creating tags...")
        for tag_name in tag_fixtures:
            try:
                Tag.objects.get_or_create(name=tag_name)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Failed to create tag {tag_name}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"  Created/verified {Tag.objects.count()} tags"))

    def create_recipes(self):
        """Generate fixture recipes and then random recipes up to RECIPE_COUNT."""
        self.generate_recipe_fixtures()
        self.generate_random_recipes()

    def create_ratings_and_favourites(self):
        """Generate ratings and favourites for all recipes."""
        self.stdout.write("Creating ratings and favourites...")
        all_recipes = list(Recipe.objects.all())
        all_users = list(User.objects.all())
        
        if not all_users or not all_recipes:
            return
        
        for recipe in all_recipes:
            num_ratings = randint(1, 10)
            
            num_ratings = min(num_ratings, len(all_users) - 1)
            
            potential_raters = [u for u in all_users if u != recipe.author]
            
            if not potential_raters:
                continue
            
            num_ratings = min(num_ratings, len(potential_raters))
            raters = sample(potential_raters, num_ratings)
            
            for user in raters:
                self.try_create_rating(recipe, user)
                
                if random() < 0.3:
                    self.try_create_favourite(recipe, user)
        
        rating_count = RecipeRating.objects.count()
        favourite_count = RecipeFavourite.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Created {rating_count} ratings and {favourite_count} favourites"))


    def generate_user_fixtures(self):
        """Attempt to create each predefined fixture user."""
        self.stdout.write("Creating fixture users...")
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_recipe_fixtures(self):
        """Attempt to create each predefined fixture recipe."""
        self.stdout.write("Creating fixture recipes...")
        for data in recipe_fixtures:
            try:
                author = User.objects.get(username=data['author'])
                recipe = self.create_recipe(data, author)
                self.stdout.write(f"  Created fixture recipe: {recipe.name}")
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Author {data['author']} not found for {data['name']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed to create {data.get('name', 'unknown')}: {e}"))

    def generate_random_users(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_random_recipes(self):
        """
        Generate random recipes until the database contains RECIPE_COUNT recipes.

        Prints a simple progress indicator to stdout during generation.
        """
        recipe_count = Recipe.objects.count()
        authors = list(User.objects.all())
        
        if not authors:
            raise CommandError("Unable to seed recipes because no authors exist.")
        
        max_attempts = self.RECIPE_COUNT * 3
        attempts = 0
        
        while recipe_count < self.RECIPE_COUNT and attempts < max_attempts:
            print(f"Seeding recipe {recipe_count}/{self.RECIPE_COUNT}", end='\r')
            author = choice(authors)
            recipe = self.try_create_recipe(author, recipe_count)
            if recipe:
                self.generate_ingredients(recipe)
                self.generate_steps(recipe)
            recipe_count = Recipe.objects.count()
            attempts += 1
        
        if attempts >= max_attempts:
            self.stdout.write(self.style.WARNING(f"\nReached max attempts ({max_attempts}). Created {recipe_count} recipes."))
        else:
            print("Recipe seeding complete.    ")

    def generate_user(self):
        """
        Generate a single random user and attempt to insert it.

        Uses Faker for first/last names, then derives a simple username/email.
        """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
    
    def generate_recipe(self, author, index):
        """Create a recipe with sensible defaults for the given author."""
        prep_minutes = randint(5, 45)
        cook_minutes = randint(10, 90)

        # Use faker food provider
        dish_name = self.faker.dish()
        description = self.faker.dish_description()
        
        recipe = Recipe.objects.create(
            author=author,
            name=dish_name,
            description=description,
            serves=randint(2, 6),
            difficulty=choice([choice[0] for choice in Recipe.DIFFICULTY_CHOICES]),
            prepTime=timedelta(minutes=prep_minutes),
            cookTime=timedelta(minutes=cook_minutes),
            cuisine=self.faker.country(),
            visibility="public",
        )
        
        self.assign_random_tags(recipe)
        
        return recipe

    def assign_random_tags(self, recipe):
        """Assign 1-4 random tags to a recipe."""
        all_tags = list(Tag.objects.all())
        if not all_tags:
            return
        
        num_tags = randint(1, min(4, len(all_tags)))
        selected_tags = sample(all_tags, num_tags)
        
        recipe.tags.set(selected_tags)

    def generate_ingredients(self, recipe):
        """Attach a random list of ingredients to a recipe."""
        ingredient_count = randint(3, 8)
        for position in range(1, ingredient_count + 1):
            ingredient = self.faker.ingredient()
            RecipeIngredient.objects.create(
                recipe=recipe,
                text=ingredient,
                position=position,
            )

    def generate_steps(self, recipe):
        """Attach a sequence of preparation steps to a recipe."""
        step_count = randint(2, 6)
        for position in range(1, step_count + 1):
            step_text = self.faker.paragraph(nb_sentences=2)
            RecipeStep.objects.create(
                recipe=recipe,
                text=step_text,
                position=position,
            )
       
    def try_create_user(self, data):
        """
        Attempt to create a user and ignore any errors.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        try:
            self.create_user(data)
        except Exception as e:
            pass

    def try_create_recipe(self, author, index):
        """
        Attempt to create a recipe and return it if successful.

        Args:
            author (User): User instance for the recipe author.
            index (int): Position used to build the display name.

        Returns:
            Recipe or None: Created recipe or None if creation failed.
        """
        try:
            return self.generate_recipe(author, index)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"\nFailed to create recipe: {e}"))
            return None

    def try_create_rating(self, recipe, user):
        """
        Attempt to create a rating for a recipe.

        Args:
            recipe (Recipe): Recipe instance to rate.
            user (User): User instance who is rating.
        """
        try:
            rating_value = randint(1, 5)
            comment = self.faker.paragraph(nb_sentences=randint(1, 3)) if random() < 0.6 else ""
            
            RecipeRating.objects.create(
                recipe=recipe,
                user=user,
                rating=rating_value,
                comment=comment,
            )
        except Exception as e:
            pass

    def try_create_favourite(self, recipe, user):
        """
        Attempt to create a favourite for a recipe.

        Args:
            recipe (Recipe): Recipe instance to favourite.
            user (User): User instance who is favouriting.
        """
        try:
            RecipeFavourite.objects.create(
                recipe=recipe,
                user=user,
            )
        except Exception as e:
            pass

    def create_user(self, data):
        """
        Create a user with the default password.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_recipe(self, data, author):
        """
        Create a recipe from fixture data with its related ingredients, steps, and tags.

        Args:
            data (dict): Recipe fixture data containing name, description, ingredients, etc.
            author (User): User instance for the recipe author.

        Returns:
            Recipe: The created recipe instance with all related objects.
        """
        recipe = Recipe.objects.create(
            author=author,
            name=data['name'],
            description=data['description'],
            serves=data['serves'],
            difficulty=data['difficulty'],
            prepTime=timedelta(minutes=data['prep_minutes']),
            cookTime=timedelta(minutes=data['cook_minutes']),
            cuisine=data['cuisine'],
            visibility=data['visibility'],
        )
        
        for position, ingredient_text in enumerate(data.get('ingredients', []), start=1):
            RecipeIngredient.objects.create(
                recipe=recipe,  
                text=ingredient_text,
                position=position,
            )
        
        for position, step_text in enumerate(data.get('steps', []), start=1):
            RecipeStep.objects.create(
                recipe=recipe,  
                text=step_text,
                position=position,
            )
        
        for tag_name in data.get('tags', []):
            tag, created = Tag.objects.get_or_create(name=tag_name)
            recipe.tags.add(tag)  
        
        return recipe


def create_username(first_name, last_name):
    """
    Construct a simple username from first and last names.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: A username in the form ``@{firstname}{lastname}`` (lowercased).
    """
    return '@' + first_name.lower() + last_name.lower()


def create_email(first_name, last_name):
    """
    Construct a simple example email address.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: An email in the form ``{firstname}.{lastname}@example.org``.
    """
    return first_name + '.' + last_name + '@example.org'