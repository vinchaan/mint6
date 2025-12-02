from django.conf import settings
from django.db import models
from django.utils import timezone


class AdminLog(models.Model):
    """Model to track all admin, moderator, and user actions for auditing purposes."""

    class ActionType(models.TextChoices):
        # User actions
        USER_CREATED = 'user_created', 'User Created'
        USER_UPDATED = 'user_updated', 'User Updated'
        USER_DELETED = 'user_deleted', 'User Deleted'
        USER_FLAGGED = 'user_flagged', 'User Flagged for Deletion'
        USER_ROLE_CHANGED = 'user_role_changed', 'User Role Changed'
        USER_LOGIN = 'user_login', 'User Login'
        USER_LOGOUT = 'user_logout', 'User Logout'
        
        # Recipe actions
        RECIPE_CREATED = 'recipe_created', 'Recipe Created'
        RECIPE_UPDATED = 'recipe_updated', 'Recipe Updated'
        RECIPE_DELETED = 'recipe_deleted', 'Recipe Deleted'
        
        # Admin actions
        ADMIN_ACTION = 'admin_action', 'Admin Action'
        MODERATOR_ACTION = 'moderator_action', 'Moderator Action'
        
        # Generic
        OTHER = 'other', 'Other'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_performed',
        help_text='The user who performed this action'
    )
    
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        default=ActionType.OTHER,
        help_text='Type of action performed'
    )
    
    target_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='Type of object affected (e.g., "User", "Recipe")'
    )
    
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID of the object affected'
    )
    
    description = models.TextField(
        help_text='Human-readable description of the action'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional structured data about the action'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the user who performed the action'
    )
    
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text='User agent string from the request'
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text='When the action was performed'
    )

    class Meta:
        """Model options."""
        
        ordering = ['-timestamp']
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['actor']),
            models.Index(fields=['action_type']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else 'System'
        return f"{actor_name} - {self.get_action_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

