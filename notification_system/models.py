import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('project_invitation', 'Project Invitation'),
        ('task_assigned', 'Task Assigned'),
        ('task_updated', 'Task Updated'),
        ('task_completed', 'Task Completed'),
        ('task_due_soon', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('comment_added', 'Comment Added'),
        ('project_updated', 'Project Updated'),
        ('member_added', 'Member Added'),
        ('member_removed', 'Member Removed'),
        ('system', 'System Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    
    # Related objects
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey('task_management.Task', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional data (JSON field for extra information)
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def time_since_created(self):
        """Human readable time since creation"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    @classmethod
    def create_notification(cls, recipient, title, message, notification_type, sender=None, project=None, task=None, extra_data=None):
        """Create a new notification"""
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            title=title,
            message=message,
            notification_type=notification_type,
            project=project,
            task=task,
            extra_data=extra_data or {}
        )
    
    @classmethod
    def create_project_invitation(cls, recipient, project, sender):
        """Create project invitation notification"""
        return cls.create_notification(
            recipient=recipient,
            sender=sender,
            title=f"Invited to {project.name}",
            message=f"You have been invited to join the project '{project.name}' by {sender.get_full_name() or sender.username}.",
            notification_type='project_invitation',
            project=project
        )
    
    @classmethod
    def create_task_assignment(cls, recipient, task, sender):
        """Create task assignment notification"""
        return cls.create_notification(
            recipient=recipient,
            sender=sender,
            title=f"New Task Assigned: {task.title}",
            message=f"You have been assigned to task '{task.title}' in project '{task.project.name}'.",
            notification_type='task_assigned',
            project=task.project,
            task=task
        )
    
    @classmethod
    def create_task_update(cls, recipient, task, sender, changes):
        """Create task update notification"""
        return cls.create_notification(
            recipient=recipient,
            sender=sender,
            title=f"Task Updated: {task.title}",
            message=f"Task '{task.title}' has been updated by {sender.get_full_name() or sender.username}.",
            notification_type='task_updated',
            project=task.project,
            task=task,
            extra_data={'changes': changes}
        )
    
    @classmethod
    def create_task_completion(cls, recipient, task, sender):
        """Create task completion notification"""
        return cls.create_notification(
            recipient=recipient,
            sender=sender,
            title=f"Task Completed: {task.title}",
            message=f"Task '{task.title}' has been marked as completed by {sender.get_full_name() or sender.username}.",
            notification_type='task_completed',
            project=task.project,
            task=task
        )
    
    @classmethod
    def create_comment_notification(cls, recipient, task, sender, comment):
        """Create comment notification"""
        return cls.create_notification(
            recipient=recipient,
            sender=sender,
            title=f"New Comment on {task.title}",
            message=f"{sender.get_full_name() or sender.username} commented on task '{task.title}'.",
            notification_type='comment_added',
            project=task.project,
            task=task,
            extra_data={'comment_id': str(comment.id)}
        )


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_project_invitations = models.BooleanField(default=True)
    email_task_assignments = models.BooleanField(default=True)
    email_task_updates = models.BooleanField(default=False)
    email_comments = models.BooleanField(default=True)
    email_due_reminders = models.BooleanField(default=True)
    
    # In-app notifications
    app_project_invitations = models.BooleanField(default=True)
    app_task_assignments = models.BooleanField(default=True)
    app_task_updates = models.BooleanField(default=True)
    app_comments = models.BooleanField(default=True)
    app_due_reminders = models.BooleanField(default=True)
    
    # Frequency settings
    digest_frequency = models.CharField(
        max_length=10,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('never', 'Never'),
        ],
        default='daily'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create notification preferences for a user"""
        preferences, created = cls.objects.get_or_create(user=user)
        return preferences
