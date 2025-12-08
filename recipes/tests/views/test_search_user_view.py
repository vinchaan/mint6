from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class SearchUserViewTest(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user1 = User.objects.create_user(username='@amy',password='Password123')
        self.user2 = User.objects.create_user(username='@bob',password='Password123')

    def test_search_successful(self):
        url = reverse('search_user')
        response = self.client.get(url, {'query': 'amy'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@amy')
        self.assertNotContains(response, '@bob')

