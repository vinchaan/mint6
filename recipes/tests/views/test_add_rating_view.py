"""Tests for the add rating view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, RecipeRating
from datetime import timedelta
from recipes.tests.helpers import LogInTester, reverse_with_next
from recipes.forms import RecipeRatingForm


class AddRatingViewTest(TestCase, LogInTester):
    """Test suite for the add rating view."""

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
        
        self.url = reverse('add_rating', kwargs={'recipe_id': self.recipe.id})
        self.valid_form_data = {
            'rating': 5,
            'comment': 'This is a great recipe!'
        }

    def test_add_rating_url(self):
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/rate/')

    def test_add_rating_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_rating_form(self):
        """Test that GET request shows the rating form."""
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_rating.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RecipeRatingForm))
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_add_rating_successfully(self):
        """Test that a user can add a rating to a recipe."""
        self.client.login(username=self.user.username, password='Password123')
        initial_count = RecipeRating.objects.count()
        initial_rating_count = self.recipe.ratingCount
        
        response = self.client.post(self.url, data=self.valid_form_data, follow=True)
        
        # Check redirect
        self.assertRedirects(response, reverse('view_recipe', kwargs={'recipe_id': self.recipe.id}), 
                           status_code=302, target_status_code=200)
        
        # Check rating was created
        self.assertEqual(RecipeRating.objects.count(), initial_count + 1)
        rating = RecipeRating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.comment, 'This is a great recipe!')
        
        # Check recipe stats updated
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, initial_rating_count + 1)
        self.assertEqual(self.recipe.averageRating, 5.0)
        
        # Check message
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertIn('added', str(messages_list[0]).lower())

    def test_update_existing_rating(self):
        """Test that a user can update their existing rating."""
        self.client.login(username=self.user.username, password='Password123')
        
        # Create initial rating
        RecipeRating.objects.create(user=self.user, recipe=self.recipe, rating=3, comment='Okay recipe')
        initial_count = RecipeRating.objects.count()
        
        # Update rating
        updated_data = {
            'rating': 5,
            'comment': 'Actually, this is great!'
        }
        response = self.client.post(self.url, data=updated_data, follow=True)
        
        # Check redirect
        self.assertRedirects(response, reverse('view_recipe', kwargs={'recipe_id': self.recipe.id}), 
                           status_code=302, target_status_code=200)
        
        # Check rating was updated (not duplicated)
        self.assertEqual(RecipeRating.objects.count(), initial_count)
        rating = RecipeRating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.comment, 'Actually, this is great!')
        
        # Check recipe stats updated
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.averageRating, 5.0)
        
        # Check message
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertIn('updated', str(messages_list[0]).lower())

    def test_rating_without_comment(self):
        """Test that a rating can be submitted without a comment."""
        self.client.login(username=self.user.username, password='Password123')
        
        data = {
            'rating': 4,
            'comment': ''
        }
        response = self.client.post(self.url, data=data, follow=True)
        
        self.assertRedirects(response, reverse('view_recipe', kwargs={'recipe_id': self.recipe.id}), 
                           status_code=302, target_status_code=200)
        
        rating = RecipeRating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.rating, 4)
        self.assertEqual(rating.comment, '')

    def test_invalid_rating_value(self):
        """Test that invalid rating values are rejected."""
        self.client.login(username=self.user.username, password='Password123')
        
        # Rating too high
        invalid_data = {
            'rating': 6,
            'comment': 'Invalid rating'
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RecipeRating.objects.filter(user=self.user, recipe=self.recipe).exists())
        
        # Rating too low
        invalid_data = {
            'rating': 0,
            'comment': 'Invalid rating'
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RecipeRating.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_multiple_users_can_rate_same_recipe(self):
        """Test that multiple users can rate the same recipe."""
        self.client.login(username=self.user.username, password='Password123')
        
        # User 1 rates
        response1 = self.client.post(self.url, data={'rating': 5, 'comment': 'Great!'}, follow=True)
        self.assertTrue(RecipeRating.objects.filter(user=self.user, recipe=self.recipe).exists())
        
        # User 2 rates
        self.client.logout()
        self.client.login(username=self.other_user.username, password='Password123')
        response2 = self.client.post(self.url, data={'rating': 4, 'comment': 'Good'}, follow=True)
        self.assertTrue(RecipeRating.objects.filter(user=self.other_user, recipe=self.recipe).exists())
        
        # Both ratings should exist
        self.assertEqual(RecipeRating.objects.filter(recipe=self.recipe).count(), 2)
        
        # Check average rating
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, 2)
        self.assertEqual(float(self.recipe.averageRating), 4.5)  # (5 + 4) / 2

    def test_rating_nonexistent_recipe(self):
        """Test that rating a non-existent recipe returns 404."""
        self.client.login(username=self.user.username, password='Password123')
        invalid_url = reverse('add_rating', kwargs={'recipe_id': 99999})
        
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_get_form_shows_existing_rating(self):
        """Test that GET request shows existing rating data."""
        self.client.login(username=self.user.username, password='Password123')
        
        # Create existing rating
        RecipeRating.objects.create(user=self.user, recipe=self.recipe, rating=3, comment='Old comment')
        
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(form.instance.rating, 3)
        self.assertEqual(form.instance.comment, 'Old comment')

