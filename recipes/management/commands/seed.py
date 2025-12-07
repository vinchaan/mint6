"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""



from faker import Faker
from random import randint, random
from django.core.management.base import BaseCommand, CommandError
from recipes.models import User
from recipes.models import (
    Recipe,
    RecipeIngredient,
    RecipeStep,
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

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        """
        self.create_users()
        self.create_recipes()
        self.users = User.objects.all()
        self.recipes = Recipe.objects.all()

    def create_users(self):
        """
        Create fixture users and then generate random users up to USER_COUNT.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on username/email) are ignored and generation continues.
        """
        self.generate_user_fixtures()
        self.generate_random_users()

    def create_recipes(self):
        """
        Create fixture recipes and then generate random recipes up to RECIPE_COUNT.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on ) are ignored and generation continues.
        """

        self.generate_recipe_fixtures()
        self.generate_random_recipes()

    def generate_user_fixtures(self):
        """Attempt to create each predefined fixture user."""
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_recipe_fixtures(self):
        for data in user_fixtures:
            self.try_create_recipe(data)

    def generate_random_users(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_random_recipes(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

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
    
    def generate_recipe(self):
        """
        Generate a single random recipe and attempt to insert it.

        Uses Faker for first/last names, then derives a simple username/email.
        """
        name = self.faker.food.dish()
        description = self.faker.food.description()
        author = 
        serves = self.random.randint(2,12)
        difficulty =                            
        prepTime = self.random.randint(15,90)
        cookTime = self.random.randint(15,180)
        totalTime = prepTime + cookTime
        cuisine = self.faker.food.ethnicCategory()
        visibility = 
        tags = 
        averageRating = round(self.random.uniform(1,5),2)
        ratingCount = self.random.randint(1,100)
        favouritesCount = self.random.randint(1,100)
        createdAt = self.faker.date.anytime()
        updatedAt = createdAt

       
    def try_create_user(self, data):
        """
        Attempt to create a user and ignore any errors.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        try:
            self.create_user(data)
        except:
            pass

    def try_create_recipe(self, data):
        """
        Attempt to create a recipe and ignore any errors.

        Args:
            data (dict): Mapping with keys .
        """
        try:
            self.create_recipe(data)
        except:
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

     def create_recipe(self, data):
        Recipe.objects.create_recipe(
            #add recipe attributes
        )

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
