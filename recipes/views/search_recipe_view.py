from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from recipes.helpers import is_admin, is_moderator
from recipes.models import Recipe, Tag


@login_required
def search_recipe(request):
    """
    Search and sort recipes based on query parameters.

    Supports searching by name, description, cuisine, author username, or tag.
    Allows filtering by difficulty, visibility, and cuisine, and supports
    sorting by common fields.
    """

    search_query = request.GET.get('q', '').strip()
    difficulty_filter = request.GET.get('difficulty', '')
    visibility_filter = request.GET.get('visibility', '')
    cuisine_filter = request.GET.get('cuisine', '').strip()
    tag_filters = request.GET.getlist('tag')
    sort_param = request.GET.get('sort', '-createdAt')

    user_is_privileged = is_admin(request.user) or is_moderator(request.user)

    base_query = Recipe.objects.all()

    if not user_is_privileged:
        base_query = base_query.filter(
            Q(visibility__in=['public', 'unlisted']) | Q(author=request.user)
        )

    recipes = base_query.select_related('author').prefetch_related('tags')

    if search_query:
        recipes = recipes.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(cuisine__icontains=search_query)
            | Q(author__username__icontains=search_query)
            | Q(tags__name__icontains=search_query)
        )

    if difficulty_filter in dict(Recipe.DIFFICULTY_CHOICES):
        recipes = recipes.filter(difficulty=difficulty_filter)

    if visibility_filter in dict(Recipe.VISIBILITY_CHOICES):
        recipes = recipes.filter(visibility=visibility_filter)
        if visibility_filter == 'private' and not user_is_privileged:
            recipes = recipes.filter(author=request.user)

    if cuisine_filter:
        recipes = recipes.filter(cuisine__icontains=cuisine_filter)

    if tag_filters:
        recipes = recipes.filter(tags__name__in=tag_filters)

    sort_options = {
        '-createdAt': 'Newest first',
        'createdAt': 'Oldest first',
        'name': 'Name A-Z',
        '-name': 'Name Z-A',
        '-averageRating': 'Rating high-low',
        'averageRating': 'Rating low-high',
        'totalTime': 'Total time low-high',
        '-totalTime': 'Total time high-low',
    }

    if sort_param not in sort_options:
        sort_param = '-createdAt'

    recipes = recipes.order_by(sort_param).distinct()

    context = {
        'recipes': recipes,
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'visibility_filter': visibility_filter,
        'cuisine_filter': cuisine_filter,
        'selected_tags': tag_filters,
        'sort_options': sort_options,
        'current_sort': sort_param,
        'available_difficulties': Recipe.DIFFICULTY_CHOICES,
        'available_visibilities': Recipe.VISIBILITY_CHOICES,
        'available_tags': Tag.objects.order_by('name'),
    }

    return render(request, 'search_recipe.html', context)

