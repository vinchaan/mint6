"""Tests for the favourite recipe view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, RecipeFavourite
from datetime import timedelta
from recipes.tests.helpers import LogInTester, reverse_with_next


class FavouriteRecipeViewTest(TestCase, LogInTester):
    """Test suite for the favourite recipe view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        
        # Create a test recipe
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='A test recipe',
            author=self.other_user,
            serves=4,
            difficulty='easy',
            prepTime=timedelta(minutes=15),
            cookTime=timedelta(minutes=30),
            visibility='public',
            cuisine='Test'
        )
        
        self.url = reverse('favourite_recipe', kwargs={'recipe_id': self.recipe.id})

    def test_favourite_recipe_url(self):
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/favourite/')

    def test_favourite_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_add_favourite_successfully(self):
        """Test that a user can add a recipe to favourites."""
        self.client.login(username=self.user.username, password='Password123')
        initial_count = RecipeFavourite.objects.count()
        
        response = self.client.post(self.url, follow=True)
        
        # Check redirect
        self.assertRedirects(response, reverse('view_recipe', kwargs={'recipe_id': self.recipe.id}), 
                           status_code=302, target_status_code=200)
        
        # Check favourite was created
        self.assertEqual(RecipeFavourite.objects.count(), initial_count + 1)
        self.assertTrue(RecipeFavourite.objects.filter(user=self.user, recipe=self.recipe).exists())
        
        # Check message
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertIn('Added', str(messages_list[0]))

    def test_remove_favourite_successfully(self):
        """Test that a user can remove a recipe from favourites."""
        self.client.login(username=self.user.username, password='Password123')
        
        # First add to favourites
        RecipeFavourite.objects.create(user=self.user, recipe=self.recipe)
        initial_count = RecipeFavourite.objects.count()
        
        # Then remove it
        response = self.client.post(self.url, follow=True)
        
        # Check redirect
        self.assertRedirects(response, reverse('view_recipe', kwargs={'recipe_id': self.recipe.id}), 
                           status_code=302, target_status_code=200)
        
        # Check favourite was removed
        self.assertEqual(RecipeFavourite.objects.count(), initial_count - 1)
        self.assertFalse(RecipeFavourite.objects.filter(user=self.user, recipe=self.recipe).exists())
        
        # Check message
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertIn('Removed', str(messages_list[0]))

    def test_favourite_updates_recipe_count(self):
        """Test that favouriting updates the recipe's favouritesCount."""
        self.client.login(username=self.user.username, password='Password123')
        initial_count = self.recipe.favouritesCount
        
        response = self.client.post(self.url, follow=True)
        
        # Refresh recipe from database
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.favouritesCount, initial_count + 1)

    def test_remove_favourite_updates_recipe_count(self):
        """Test that removing favourite updates the recipe's favouritesCount."""
        self.client.login(username=self.user.username, password='Password123')
        
        # First add to favourites
        RecipeFavourite.objects.create(user=self.user, recipe=self.recipe)
        self.recipe.refresh_from_db()
        initial_count = self.recipe.favouritesCount
        
        # Then remove it
        response = self.client.post(self.url, follow=True)
        
        # Refresh recipe from database
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.favouritesCount, initial_count - 1)

    def test_favourite_nonexistent_recipe(self):
        """Test that favouriting a non-existent recipe returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        invalid_url = reverse('favourite_recipe', kwargs={'recipe_id': 99999})
        
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_multiple_users_can_favourite_same_recipe(self):
        """Test that multiple users can favourite the same recipe."""
        self.client.login(username=self.user.username, password='Password123')
        
        # User 1 favourites
        response1 = self.client.post(self.url, follow=True)
        self.assertTrue(RecipeFavourite.objects.filter(user=self.user, recipe=self.recipe).exists())
        
        # User 2 favourites
        self.client.logout()
        self.client.login(username=self.other_user.username, password='Password123')
        response2 = self.client.post(self.url, follow=True)
        self.assertTrue(RecipeFavourite.objects.filter(user=self.other_user, recipe=self.recipe).exists())
        
        # Both favourites should exist
        self.assertEqual(RecipeFavourite.objects.filter(recipe=self.recipe).count(), 2)

