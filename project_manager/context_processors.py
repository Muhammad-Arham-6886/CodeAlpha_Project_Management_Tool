"""
Context processors for global template variables
"""

def notification_count(request):
    """
    Add unread notification count to template context
    """
    if request.user.is_authenticated:
        try:
            from notification_system.models import Notification
            unread_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
        except Exception:
            # Handle case where notification_system might not be available
            return {'unread_notifications_count': 0}
    return {'unread_notifications_count': 0}
