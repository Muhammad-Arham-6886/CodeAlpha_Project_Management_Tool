from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipient', 'sender', 'title', 'message', 'notification_type')
        }),
        ('Related Objects', {
            'fields': ('project', 'task')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Additional Data', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                updated += 1
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = 0
        for notification in queryset:
            if notification.is_read:
                notification.mark_as_unread()
                updated += 1
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'digest_frequency', 'created_at', 'updated_at']
    list_filter = ['digest_frequency', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_project_invitations',
                'email_task_assignments',
                'email_task_updates',
                'email_comments',
                'email_due_reminders',
            )
        }),
        ('In-App Notifications', {
            'fields': (
                'app_project_invitations',
                'app_task_assignments',
                'app_task_updates',
                'app_comments',
                'app_due_reminders',
            )
        }),
        ('Settings', {
            'fields': ('digest_frequency',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
