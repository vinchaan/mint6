from recipes.models import User


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