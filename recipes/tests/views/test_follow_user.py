from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class FollowUserViewTest(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(username='@follower', password='Password123')
        self.target_user = User.objects.create_user(username='@target', password='Password123')

        self.client.force_login(self.user)

    def test_follow_user_successfully(self):
        self.assertEqual(self.target_user.followers.count(), 0)
        url = reverse('follow_user', kwargs={'pk': self.target_user.pk})
        response = self.client.get(url)

        # Check for Redirection (302)
        self.assertEqual(response.status_code, 302)

        # Check it redirects to the profile page
        expected_url = reverse('profile', kwargs={'pk': self.target_user.pk})
        self.assertRedirects(response, expected_url)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.followers.count(), 1)
        self.assertIn(self.user, self.target_user.followers.all())

    def test_unfollow_user_successfully(self):
        self.target_user.followers.add(self.user)
        self.assertEqual(self.target_user.followers.count(), 1)

        url = reverse('follow_user', kwargs={'pk': self.target_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.followers.count(), 0)
        self.assertNotIn(self.user, self.target_user.followers.all())

    def test_follow_non_existent_user(self):
        non_existent_pk = 9999
        url = reverse('follow_user', kwargs={'pk': non_existent_pk})

        with self.assertRaises(get_user_model().DoesNotExist):
            self.client.get(url)