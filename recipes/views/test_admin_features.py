from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from recipes.models import Recipe

class AdminFeatureTests(TestCase):
    def setUp(self):
        # 1. Create a Superuser 
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='password123'
        )
        
        # 2. Create a Regular User
        self.regular_user = User.objects.create_user(
            username='regular', 
            email='regular@test.com', 
            password='password123'
        )

        # 3. Create a Recipe 
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='Test Description',
            cooking_time=10,
            difficulty='Easy',
            author=self.regular_user
        )

        # 4. Set up the client
        self.client = Client()

    # Testing Admin Delete Function
    def test_admin_can_delete_recipe(self):
        """Test that an admin can delete any recipe."""
        self.client.login(username='admin', password='password123')
        
        url = reverse('delete_recipe_admin', args=[self.recipe.id])
        response = self.client.get(url) 

        self.assertEqual(response.status_code, 302) 
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_regular_user_cannot_delete_via_admin_url(self):
        """Test that a regular user CANNOT use the admin delete URL."""
        self.client.login(username='regular', password='password123')
        
        url = reverse('delete_recipe_admin', args=[self.recipe.id])
        response = self.client.get(url)

        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())

    # Testing Search User Function
    def test_admin_search_user(self):
        """Test that searching for a user returns the correct result."""
        self.client.login(username='admin', password='password123')
        
        url = reverse('admin_panel') + '?q=regular'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.regular_user, response.context['users'])

    # Testing Sort User Function
    def test_admin_sort_users(self):
        """Test that sorting users works."""
        User.objects.create_user(username='zara', email='zara@test.com', password='pw')
        
        self.client.login(username='admin', password='password123')
        
        url = reverse('admin_panel') + '?sort=username'
        response = self.client.get(url)
        
        users_list = list(response.context['users'])
    
        self.assertTrue(users_list[0].username < users_list[1].username)