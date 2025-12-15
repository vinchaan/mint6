from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib.auth import get_user_model 
from recipes.helpers import is_admin, is_moderator
from recipes.models import Recipe, Tag

# Get the correct User model (recipes.User) instead of the default auth.User
User = get_user_model() 

@login_required
def admin_panel(request):
    """
    Admin panel view - accessible to admins and moderators.
    Shows both users and recipes management in a tabbed interface.
    """
    
    # Check if user has admin or moderator privileges
    if not (is_admin(request.user) or is_moderator(request.user)):
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('dashboard')

    # Get active tab from URL parameter
    # Default to 'recipes' for moderators, 'users' for admins
    if is_admin(request.user):
        active_tab = request.GET.get('tab', 'users')
    else:
        active_tab = request.GET.get('tab', 'recipes')
    
    # --- User Search & Sort Logic ---
    users = User.objects.all()
    user_search_query = request.GET.get('q', '')
    if user_search_query:
        users = users.filter(
            Q(username__icontains=user_search_query) | 
            Q(email__icontains=user_search_query)
        )
    
    user_sort_param = request.GET.get('sort', 'username')
    valid_user_sort_fields = ['username', 'email', 'date_joined', 'is_active']
    if user_sort_param in valid_user_sort_fields:
        users = users.order_by(user_sort_param)
    
    # --- Recipe Search & Filter Logic ---
    recipes = Recipe.objects.all().select_related('author').prefetch_related('tags')
    
    recipe_search_query = request.GET.get('rq', '')
    if recipe_search_query:
        recipes = recipes.filter(
            Q(name__icontains=recipe_search_query) |
            Q(description__icontains=recipe_search_query) |
            Q(author__username__icontains=recipe_search_query) |
            Q(tags__name__icontains=recipe_search_query)
        )
    
    recipe_difficulty = request.GET.get('difficulty', '')
    if recipe_difficulty in dict(Recipe.DIFFICULTY_CHOICES):
        recipes = recipes.filter(difficulty=recipe_difficulty)
    
    recipe_visibility = request.GET.get('visibility', '')
    if recipe_visibility in dict(Recipe.VISIBILITY_CHOICES):
        recipes = recipes.filter(visibility=recipe_visibility)
    
    recipe_sort_param = request.GET.get('rsort', '-createdAt')
    valid_recipe_sorts = ['-createdAt', 'createdAt', 'name', '-name', '-averageRating', 'averageRating']
    if recipe_sort_param in valid_recipe_sorts:
        recipes = recipes.order_by(recipe_sort_param)
    else:
        recipes = recipes.order_by('-createdAt')
    
    recipes = recipes.distinct()
    
    return render(request, 'admin_panel.html', {
        'user': request.user,
        'users': users,
        'recipes': recipes,
        'user_search_query': user_search_query,
        'recipe_search_query': recipe_search_query,
        'user_sort': user_sort_param,
        'recipe_sort': recipe_sort_param,
        'recipe_difficulty': recipe_difficulty,
        'recipe_visibility': recipe_visibility,
        'active_tab': active_tab,
        'available_difficulties': Recipe.DIFFICULTY_CHOICES,
        'available_visibilities': Recipe.VISIBILITY_CHOICES,
        'available_tags': Tag.objects.order_by('name'),
    })