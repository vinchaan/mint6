from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from recipes.helpers import is_admin, is_moderator
from recipes.models import AdminLog


@login_required
def view_logs(request):
    """
    View logs with enhanced search and filtering.
    
    Accessible to admins and moderators. Provides search and filter
    capabilities for viewing action logs.
    """
    
    # Check if user has admin or moderator privileges
    if not (is_admin(request.user) or is_moderator(request.user)):
        messages.error(request, "You do not have permission to view logs.")
        return redirect('dashboard')
    
    # Get all logs
    logs = AdminLog.objects.all().select_related('actor').order_by('-timestamp')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        logs = logs.filter(
            Q(description__icontains=search_query) |
            Q(actor__username__icontains=search_query) |
            Q(actor__email__icontains=search_query) |
            Q(target_type__icontains=search_query) |
            Q(action_type__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    # Filter by action type
    action_type_filter = request.GET.get('action_type', '')
    if action_type_filter:
        logs = logs.filter(action_type=action_type_filter)
    
    # Filter by target type
    target_type_filter = request.GET.get('target_type', '')
    if target_type_filter:
        logs = logs.filter(target_type=target_type_filter)
    
    # Filter by actor
    actor_filter = request.GET.get('actor', '')
    if actor_filter:
        try:
            logs = logs.filter(actor_id=int(actor_filter))
        except (ValueError, TypeError):
            actor_filter = ''
    
    # Date range filtering
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Pagination
    paginator = Paginator(logs, 50)  # Show 50 logs per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filter dropdowns
    action_types = AdminLog.objects.values_list('action_type', flat=True).distinct().order_by('action_type')
    target_types = AdminLog.objects.exclude(target_type='').values_list('target_type', flat=True).distinct().order_by('target_type')
    
    # Get actors for filter (users who have performed actions)
    actors = AdminLog.objects.exclude(actor=None).select_related('actor').values_list('actor_id', 'actor__username').distinct().order_by('actor__username')
    
    context = {
        'logs': page_obj,
        'search_query': search_query,
        'action_type_filter': action_type_filter,
        'target_type_filter': target_type_filter,
        'actor_filter': actor_filter,
        'date_from': date_from,
        'date_to': date_to,
        'action_types': action_types,
        'target_types': target_types,
        'actors': actors,
        'action_type_choices': AdminLog.ActionType.choices,
    }
    
    return render(request, 'logs.html', context)

