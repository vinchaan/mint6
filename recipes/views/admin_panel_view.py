from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from recipes.helpers import is_admin, is_moderator


@login_required
def admin_panel(request):
    """
    Admin panel view - accessible to admins and moderators.
    
    This view displays the admin panel with various administrative options.
    Only admins and moderators can access this page.
    """
    
    # Check if user has admin or moderator privileges
    if not (is_admin(request.user) or is_moderator(request.user)):
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('dashboard')
    
    return render(request, 'admin_panel.html', {
        'user': request.user,
    })

