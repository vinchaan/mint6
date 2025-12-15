from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from recipes.models import Recipe, RecipeRating, RecipeFavourite, Tag


User = get_user_model()


class RecipeStatsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='@author',
            email='author@test.com',
            password='Password123',
        )
        self.user1 = User.objects.create_user(
            username='@user1',
            email='user1@test.com',
            password='Password123',
        )
        self.user2 = User.objects.create_user(
            username='@user2',
            email='user2@test.com',
            password='Password123',
        )

        self.recipe = Recipe.objects.create(
            author=self.author,
            name="Test Recipe",
            description="Desc",
            serves=2,
            difficulty="easy",
            prepTime=timedelta(minutes=10),
            cookTime=timedelta(minutes=20),
            cuisine="British",
            visibility="public",
        )

    def test_total_time_is_computed_on_save(self):
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.totalTime, timedelta(minutes=30))

    def test_update_rating_stats_no_ratings(self):
        self.recipe.update_rating_stats()
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, 0)
        self.assertEqual(Decimal(str(self.recipe.averageRating)), Decimal("0"))

    def test_rating_create_updates_stats(self):
        RecipeRating.objects.create(recipe=self.recipe, user=self.user1, rating=5, comment="")
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, 1)
        self.assertEqual(Decimal(str(self.recipe.averageRating)), Decimal("5.0"))

    def test_rating_update_updates_stats(self):
        r = RecipeRating.objects.create(recipe=self.recipe, user=self.user1, rating=5)
        r.rating = 3
        r.save()

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, 1)
        self.assertEqual(Decimal(str(self.recipe.averageRating)), Decimal("3.0"))

    def test_rating_delete_updates_stats(self):
        r1 = RecipeRating.objects.create(recipe=self.recipe, user=self.user1, rating=5)
        r2 = RecipeRating.objects.create(recipe=self.recipe, user=self.user2, rating=1)

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, 2)
        self.assertEqual(Decimal(str(self.recipe.averageRating)), Decimal("3.0"))

        r2.delete()

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ratingCount, 1)
        self.assertEqual(Decimal(str(self.recipe.averageRating)), Decimal("5.0"))

    def test_unique_rating_per_user_per_recipe(self):
        RecipeRating.objects.create(recipe=self.recipe, user=self.user1, rating=4)
        with self.assertRaises(Exception):
            RecipeRating.objects.create(recipe=self.recipe, user=self.user1, rating=5)

    def test_favourite_create_updates_count(self):
        RecipeFavourite.objects.create(recipe=self.recipe, user=self.user1)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.favouritesCount, 1)

    def test_favourite_delete_updates_count(self):
        fav = RecipeFavourite.objects.create(recipe=self.recipe, user=self.user1)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.favouritesCount, 1)

        fav.delete()
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.favouritesCount, 0)

    def test_unique_favourite_per_user_per_recipe(self):
        RecipeFavourite.objects.create(recipe=self.recipe, user=self.user1)
        with self.assertRaises(Exception):
            RecipeFavourite.objects.create(recipe=self.recipe, user=self.user1)

    def test_assign_tags(self):
        t1 = Tag.objects.create(name="Quick")
        t2 = Tag.objects.create(name="Family")
        self.recipe.tags.set([t1, t2])
        self.assertEqual(self.recipe.tags.count(), 2)
