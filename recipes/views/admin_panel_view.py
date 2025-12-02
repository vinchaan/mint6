from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model  # <--- CHANGED IMPORT
from recipes.helpers import is_admin, is_moderator

# Get the correct User model (recipes.User) instead of the default auth.User
User = get_user_model()  # <--- ADDED THIS LINE

@login_required
def admin_panel(request):
    """
    Admin panel view - accessible to admins and moderators.
    """
    
    # Check if user has admin or moderator privileges
    if not (is_admin(request.user) or is_moderator(request.user)):
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('dashboard')

    # --- User Search & Sort Logic ---
    
    # 1. Start with all users
    users = User.objects.all()

    # 2. Search Functionality
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query)
        )

    # 3. Sort Functionality
    sort_param = request.GET.get('sort', 'username') # Default sort
    valid_sort_fields = ['username', 'email', 'date_joined', 'is_active']
    
    if sort_param in valid_sort_fields:
        users = users.order_by(sort_param)

    # --- END NEW CODE ---
    
    return render(request, 'admin_panel.html', {
        'user': request.user,
        'users': users,
        'search_query': search_query,
        'current_sort': sort_param,
    })