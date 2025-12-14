from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from recipes.helpers import can_delete_user, log_action
from recipes.models import User, AdminLog


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
    
    # Safety checks
    # Prevent deleting yourself
    if request.user.id == target_user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('dashboard')
    
    # Prevent deleting other admins
    if target_user.is_admin:
        messages.error(request, "You cannot delete other admin accounts.")
        return redirect('dashboard')
    
    # Log the action
    log_action(
        actor=request.user,
        action_type=AdminLog.ActionType.USER_DELETED,
        description=f"{request.user.username} deleted user {target_user.username} (ID: {target_user.id})",
        target_type='User',
        target_id=target_user.id,
        metadata={
            'target_username': target_user.username,
            'target_email': target_user.email,
            'target_role': target_user.role,
        },
        request=request,
    )
    
    # Delete the user
    target_user.delete()
    messages.success(request, f"User '{target_user.username}' has been deleted.")
    return redirect('home')

