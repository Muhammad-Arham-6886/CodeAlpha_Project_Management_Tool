from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from projects.models import Project
from task_management.models import Task
from django.utils import timezone
from datetime import timedelta


@login_required
def reports_dashboard(request):
    """Main reports dashboard view"""
    # Get user's projects and tasks
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    user_tasks = Task.objects.filter(
        Q(created_by=request.user) | Q(assigned_to=request.user)
    ).distinct()
    
    # Calculate statistics
    stats = {
        'total_projects': user_projects.count(),
        'active_projects': user_projects.filter(status='active').count(),
        'completed_projects': user_projects.filter(status='completed').count(),
        'total_tasks': user_tasks.count(),
        'completed_tasks': user_tasks.filter(status='completed').count(),
        'overdue_tasks': user_tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=['todo', 'in_progress']
        ).count(),
    }
    
    # Calculate completion rates
    stats['project_completion_rate'] = (
        (stats['completed_projects'] / stats['total_projects'] * 100) 
        if stats['total_projects'] > 0 else 0
    )
    stats['task_completion_rate'] = (
        (stats['completed_tasks'] / stats['total_tasks'] * 100) 
        if stats['total_tasks'] > 0 else 0
    )
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_projects = user_projects.filter(created_at__gte=thirty_days_ago).count()
    recent_tasks = user_tasks.filter(created_at__gte=thirty_days_ago).count()
    
    # Project status distribution
    project_status_data = list(user_projects.values('status').annotate(count=Count('status')))
    
    # Task priority distribution
    task_priority_data = list(user_tasks.values('priority').annotate(count=Count('priority')))
    
    context = {
        'stats': stats,
        'recent_projects': recent_projects,
        'recent_tasks': recent_tasks,
        'project_status_data': project_status_data,
        'task_priority_data': task_priority_data,
    }
    
    return render(request, 'project_reports/dashboard.html', context)
