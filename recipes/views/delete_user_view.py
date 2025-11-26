from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from recipes.helpers import can_delete_user
from recipes.models import User


@login_required
def delete_user(request, user_id):
    """
    Delete a user (admin only).
    
    This view allows admins to delete any user account.
    Moderators and regular users are redirected with an error message.
    """
    
    # Checks if user has permission to delete users
    if not can_delete_user(request.user):
        messages.error(request, "You do not have permission to delete users.")
        return redirect('dashboard')
    
    # Gets the target user object
    target_user = get_object_or_404(User, pk=user_id)
    
    # TODO: Safety checks
    # prevent deleting yourself
    # prevent deleting other admins?
    # check if user has important data that should be preserved?
    
    # TODO: Uncomment when ready to actually delete
    # target_user.delete()
    # messages.success(request, f"User '{target_user.username}' has been deleted.")
    
    # For now, just redirect (skeleton code)
    messages.info(request, f"User deletion for '{target_user.username}' would happen here.")
    return redirect('dashboard')
    
    # TODO: Redirecting to a user management page
    # return redirect(reverse('user_list'))  # if you have a user list view

