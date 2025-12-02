from typing import Optional, Dict, Any
from django.http import HttpRequest
from recipes.models import User, AdminLog


def is_admin(user: User) -> bool:
    """Return True if the user has the admin role."""

    return bool(user and user.is_authenticated and user.is_admin)


def is_moderator(user: User) -> bool:
    """Return True if the user has the moderator role."""

    return bool(user and user.is_authenticated and user.is_moderator)


def can_delete_recipe(user: User) -> bool:
    """
    Admins and moderators can delete recipes.
    """

    return is_admin(user) or is_moderator(user)


def can_delete_user(user: User) -> bool:
    """
    Only admins can delete users.
    """

    return is_admin(user)


def can_flag_user_for_deletion(user: User) -> bool:
    """
    Admins and moderators can flag users for deletion.

    """

    return is_moderator(user)


def log_action(
    actor: Optional[User],
    action_type: str,
    description: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request: Optional[HttpRequest] = None,
) -> AdminLog:
    """
    Log an action performed by a user, moderator, or admin.
    
    Args:
        actor: The user who performed the action (None for system actions)
        action_type: Type of action (should be from AdminLog.ActionType)
        description: Human-readable description of the action
        target_type: Type of object affected (e.g., 'User', 'Recipe')
        target_id: ID of the object affected
        metadata: Additional structured data about the action
        request: Optional HttpRequest to extract IP and user agent
    
    Returns:
        The created AdminLog instance
    """
    ip_address = None
    user_agent = ''
    
    if request:
        # Get IP address from request
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    log_entry = AdminLog.objects.create(
        actor=actor,
        action_type=action_type,
        target_type=target_type or '',
        target_id=target_id,
        description=description,
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return log_entry


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Extract the client IP address from a request.
    
    Args:
        request: The HttpRequest object
    
    Returns:
        The IP address as a string, or None if not available
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')