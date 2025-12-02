from django.contrib import admin
from django.utils.html import format_html
from recipes.models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """Admin interface for viewing action logs."""
    
    list_display = [
        'timestamp',
        'actor_display',
        'action_type_display',
        'target_display',
        'description_short',
        'ip_address',
    ]
    
    list_filter = [
        'action_type',
        'target_type',
        ('actor', admin.RelatedOnlyFieldListFilter),
        ('timestamp', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'actor__username',
        'actor__email',
        'description',
        'target_type',
        'ip_address',
        'action_type',
    ]
    
    readonly_fields = [
        'actor',
        'action_type',
        'target_type',
        'target_id',
        'description',
        'metadata',
        'ip_address',
        'user_agent',
        'timestamp',
        'metadata_display',
    ]
    
    date_hierarchy = 'timestamp'
    
    ordering = ['-timestamp']
    
    def actor_display(self, obj):
        """Display actor with link if available."""
        if obj.actor:
            return format_html(
                '<a href="/admin/recipes/user/{}/change/">{}</a>',
                obj.actor.id,
                obj.actor.username
            )
        return 'System'
    actor_display.short_description = 'Actor'
    
    def action_type_display(self, obj):
        """Display action type with badge."""
        colors = {
            'user_deleted': 'red',
            'user_flagged': 'orange',
            'recipe_deleted': 'red',
            'user_created': 'green',
            'recipe_created': 'green',
        }
        color = colors.get(obj.action_type, 'blue')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_type_display()
        )
    action_type_display.short_description = 'Action'
    
    def target_display(self, obj):
        """Display target object."""
        if obj.target_type and obj.target_id:
            return f"{obj.target_type} #{obj.target_id}"
        return '-'
    target_display.short_description = 'Target'
    
    def description_short(self, obj):
        """Display truncated description."""
        if len(obj.description) > 60:
            return obj.description[:60] + '...'
        return obj.description
    description_short.short_description = 'Description'
    
    def metadata_display(self, obj):
        """Display metadata in a readable format."""
        if obj.metadata:
            import json
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>',
                json.dumps(obj.metadata, indent=2)
            )
        return '-'
    metadata_display.short_description = 'Metadata'
    
    def has_add_permission(self, request):
        """Prevent manual creation of log entries."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of log entries."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow admins to delete logs."""
        return request.user.is_superuser
