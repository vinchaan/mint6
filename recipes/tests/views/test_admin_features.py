from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()

class AdminFeatureTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='password123'
        )
        self.regular_user = User.objects.create_user(
            username='regular', email='regular@test.com', password='password123'
        )
        self.recipe = Recipe.objects.create(
            name='Test Recipe', description='Desc', author=self.regular_user,
            serves=4, difficulty='easy', visibility='public',
            prepTime=timedelta(minutes=10), cookTime=timedelta(minutes=20)
        )
        self.client = Client()

    # Testing admin delete
    @patch('recipes.views.delete_recipe_view.check_admin', return_value=True)
    def test_admin_can_delete_recipe(self, mock_check):
        self.client.force_login(self.admin_user)
        
        url = reverse('delete_recipe_admin', args=[self.recipe.id])
        print(f"\nTesting URL: {url}")

        response = self.client.get(url, follow=True)
        
        print(f"Response Status: {response.status_code}")
        print(f"Redirect Chain: {response.redirect_chain}")

        exists = Recipe.objects.filter(id=self.recipe.id).exists()
        print(f"Recipe exists after delete? {exists}")
        
        self.assertFalse(exists)

    # Testing search function 
    @patch('recipes.views.admin_panel_view.is_admin', return_value=True)
    @patch('recipes.views.admin_panel_view.is_moderator', return_value=True)
    def test_admin_search_user(self, mock_is_mod, mock_is_admin):
        self.client.force_login(self.admin_user)
        url = reverse('admin_panel') + '?q=regular'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.regular_user, response.context['users'])

    # Testing sort function
    @patch('recipes.views.admin_panel_view.is_admin', return_value=True)
    @patch('recipes.views.admin_panel_view.is_moderator', return_value=True)
    def test_admin_sort_users(self, mock_is_mod, mock_is_admin):
        User.objects.create_user(username='zara', email='zara@test.com', password='pw')
        self.client.force_login(self.admin_user)
        url = reverse('admin_panel') + '?sort=username'
        response = self.client.get(url)
        users = list(response.context['users'])
        self.assertTrue(users[0].username < users[1].username)

    def test_regular_user_cannot_delete_via_admin_url(self):
        self.client.force_login(self.regular_user)
        url = reverse('delete_recipe_admin', args=[self.recipe.id])
        self.client.get(url)
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())