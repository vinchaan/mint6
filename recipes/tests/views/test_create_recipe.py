from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()

class CreateRecipeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='chef', 
            email='chef@test.com', 
            password='password123'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('create_recipe')

    def test_create_recipe_success(self):
        """Test that valid data creates a new recipe."""
        
        form_data = {
            'name': 'Spaghetti Carbonara',
            'description': 'Classic Italian pasta.',
            'serves': 4,
            'difficulty': 'medium',
            'visibility': 'public',
            'prepTime': '00:15:00',
            'cookTime': '00:20:00',
            'cuisine': 'Italian',
            'tags': [], 
            
            'ingredients-TOTAL_FORMS': '1',
            'ingredients-INITIAL_FORMS': '0',
            'ingredients-MIN_NUM_FORMS': '0',
            'ingredients-MAX_NUM_FORMS': '1000',
            'ingredients-0-text': '200g Pasta',

            'steps-TOTAL_FORMS': '1',
            'steps-INITIAL_FORMS': '0',
            'steps-MIN_NUM_FORMS': '0',
            'steps-MAX_NUM_FORMS': '1000',
            'steps-0-text': 'Boil water.',
        }
        
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 200)
     
        self.assertTrue(Recipe.objects.filter(name='Spaghetti Carbonara').exists())
        
        recipe = Recipe.objects.get(name='Spaghetti Carbonara')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.serves, 4)

    def test_create_recipe_invalid(self):
        """Test that missing required fields prevents creation."""
        invalid_data = {
            'name': 'Incomplete Recipe',
            'description': 'This should fail',
        }
        
        response = self.client.post(self.url, data=invalid_data)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(Recipe.objects.filter(name='Incomplete Recipe').exists())