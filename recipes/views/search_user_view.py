from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

def search_user(request):
    User = get_user_model()

    search_query = request.GET.get('query', '')
    sort_by = request.GET.get('sort', 'username')  # Default sort by username
    filter_type = request.GET.get('filter', 'all')  # Filter type: all, active, new
    
    # Base queryset
    users = User.objects.all()
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply additional filters
    if filter_type == 'active':
        # Users with most recipes (most active)
        users = users.annotate(recipe_count=Count('recipes')).filter(recipe_count__gt=0).order_by('-recipe_count')
    elif filter_type == 'new':
        # Newest users first
        users = users.order_by('-date_joined')
    
    # Apply sorting
    valid_sort_fields = ['username', 'email', 'date_joined']
    if sort_by in valid_sort_fields:
        if filter_type != 'active' and filter_type != 'new':  # Don't override filter sorting
            users = users.order_by(sort_by)
    
    # Annotate with recipe count for display
    users = users.annotate(recipe_count=Count('recipes'))

    return render(request, 'search_user.html', {
        'results': users,
        'search_query': search_query,
        'sort_by': sort_by,
        'filter_type': filter_type,
    })