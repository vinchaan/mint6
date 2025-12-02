from functools import wraps
from typing import Optional, Callable, Any
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from recipes.helpers import log_action
from recipes.models import AdminLog


def login_prohibited(view_function):
    """
    Decorator that prevents logged-in users from accessing a view.

    This decorator is typically used for pages such as login or registration,
    where it doesn't make sense for an authenticated user to remain.
    If the user is already authenticated, they are redirected to the URL
    defined in `settings.REDIRECT_URL_WHEN_LOGGED_IN`.

    Args:
        view_function (Callable): The Django view function being decorated.

    Returns:
        Callable: A wrapped view function that either redirects an authenticated
        user or calls the original view for unauthenticated users.

    Raises:
        ImproperlyConfigured: If `settings.REDIRECT_URL_WHEN_LOGGED_IN` is not defined.
    """
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function


class LoginProhibitedMixin:
    """
    Mixin that prevents logged-in users from accessing certain class-based views.

    This mixin is useful for class-based views such as LoginView or SignupView,
    where authenticated users should not be able to access the page. It redirects
    them to a specified URL instead.

    Attributes:
        redirect_when_logged_in_url (str): Optional. The URL to redirect to if
            the user is already logged in. Must be defined either as a class
            attribute or by overriding `get_redirect_when_logged_in_url()`.
    """

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """
        Intercept requests before they reach the view handler.

        If the user is authenticated, redirects them using
        `handle_already_logged_in()`. Otherwise, proceeds normally.
        """
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        """
        Redirect the user when already logged in.
        """
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """
        Determine the redirect URL for authenticated users.

        If the `redirect_when_logged_in_url` attribute is not defined,
        this method must be overridden in a subclass. Otherwise, an
        `ImproperlyConfigured` exception is raised.
        """
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


def log_admin_action(
    action_type: str,
    description_template: Optional[str] = None,
    target_type: Optional[str] = None,
    get_target_id: Optional[Callable] = None,
):
    """
    Decorator to automatically log admin/moderator actions.
    
    Args:
        action_type: Type of action (from AdminLog.ActionType)
        description_template: Template string for description (can use {actor}, {target}, etc.)
        target_type: Type of target object (e.g., 'User', 'Recipe')
        get_target_id: Optional function to extract target_id from view kwargs
    
    Example:
        @log_admin_action(
            action_type=AdminLog.ActionType.USER_DELETED,
            description_template="{actor} deleted user {target}",
            target_type='User',
            get_target_id=lambda kwargs: kwargs.get('user_id')
        )
        def delete_user(request, user_id):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Execute the view first
            response = view_func(request, *args, **kwargs)
            
            # Extract target_id if function provided
            target_id = None
            if get_target_id:
                try:
                    target_id = get_target_id(kwargs)
                except (KeyError, AttributeError):
                    pass
            
            # Generate description
            if description_template:
                actor_name = request.user.username if request.user.is_authenticated else 'System'
                target_name = f"#{target_id}" if target_id else "unknown"
                description = description_template.format(
                    actor=actor_name,
                    target=target_name,
                    **kwargs
                )
            else:
                description = f"{view_func.__name__} action performed"
            
            # Log the action
            try:
                log_action(
                    actor=request.user if request.user.is_authenticated else None,
                    action_type=action_type,
                    description=description,
                    target_type=target_type,
                    target_id=target_id,
                    request=request,
                )
            except Exception:
                # Don't let logging errors break the view
                pass
            
            return response
        return wrapper
    return decorator