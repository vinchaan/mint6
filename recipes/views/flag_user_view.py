from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from recipes.helpers import can_flag_user_for_deletion
from recipes.models import User


@login_required
def flag_user_for_deletion(request, user_id):
    """
    Flag a user for deletion (admin and moderator only).
    
    This view allows admins and moderators to flag users for deletion.
    The actual deletion would be handled by an admin later.
    Regular users are redirected with an error message.
    """
    
    # Checks if user has permission to flag users
    if not can_flag_user_for_deletion(request.user):
        messages.error(request, "You do not have permission to flag users for deletion.")
        return redirect('dashboard')
    
    # Get the target user object
    target_user = get_object_or_404(User, pk=user_id)
    
    # TODO: Add a field to User model to track flagged status
    # flagged_for_deletion = models.BooleanField(default=False)

    # after that uncomment below

    # target_user.flagged_for_deletion = True
    # target_user.save()
    # messages.success(request, f"User '{target_user.username}' has been flagged for deletion.")
    
    # For now, just redirect (skeleton code)
    messages.info(request, f"Flagging user '{target_user.username}' for deletion would happen here.")
    return redirect('dashboard')
    
    # TODO: Redirecting to a user management page
    # return redirect(reverse('user_list'))  # if you have a user list view

