from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe, User


class SearchRecipeViewTests(TestCase):
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.url = reverse('search_recipe')
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.client.login(username=self.user.username, password='Password123')

        self.recipe_easy = Recipe.objects.create(
            name='Spicy Curry',
            description='A hot curry with chili and garlic.',
            author=self.user,
            serves=2,
            difficulty='easy',
            visibility='public',
            prepTime=timedelta(minutes=10),
            cookTime=timedelta(minutes=20),
            cuisine='Indian',
            averageRating=Decimal('4.5'),
        )
        self.recipe_medium = Recipe.objects.create(
            name='Lemon Pie',
            description='Fresh lemon dessert.',
            author=self.other_user,
            serves=6,
            difficulty='medium',
            visibility='public',
            prepTime=timedelta(minutes=15),
            cookTime=timedelta(minutes=30),
            cuisine='French',
            averageRating=Decimal('3.0'),
        )
        self.private_recipe = Recipe.objects.create(
            name='Secret Stew',
            description='Hidden recipe for family only.',
            author=self.third_user,
            serves=4,
            difficulty='hard',
            visibility='private',
            prepTime=timedelta(minutes=20),
            cookTime=timedelta(minutes=40),
            cuisine='Fusion',
            averageRating=Decimal('5.0'),
        )

    def test_search_recipe_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_search_recipe_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_recipe.html')
        self.assertIn('recipes', response.context)

    def test_search_filters_by_query(self):
        response = self.client.get(self.url + '?q=curry')
        self.assertIn(self.recipe_easy, response.context['recipes'])
        self.assertNotIn(self.recipe_medium, response.context['recipes'])

    def test_sorting_by_rating_desc(self):
        response = self.client.get(self.url + '?sort=-averageRating')
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], self.recipe_easy)
        self.assertNotIn(self.private_recipe, recipes)

    def test_filter_by_difficulty(self):
        response = self.client.get(self.url + '?difficulty=medium')
        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe_medium, recipes)
        self.assertNotIn(self.recipe_easy, recipes)

    def test_private_recipes_only_visible_to_author(self):
        response = self.client.get(self.url)
        self.assertNotIn(self.private_recipe, response.context['recipes'])

        self.client.logout()
        self.client.login(username=self.third_user.username, password='Password123')
        response = self.client.get(self.url + '?visibility=private')
        self.assertIn(self.private_recipe, response.context['recipes'])

