from django.contrib.auth import logout
from django.shortcuts import redirect
from recipes.helpers import log_action
from recipes.models import AdminLog


def log_out(request):
    """Log out the current user"""
    
    # Log the logout action before logging out
    if request.user.is_authenticated:
        log_action(
            actor=request.user,
            action_type=AdminLog.ActionType.USER_LOGOUT,
            description=f"{request.user.username} logged out",
            request=request,
        )
    
    logout(request)
    return redirect('home')