from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Count, Case, When, IntegerField
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .models import Task, TaskComment, TaskActivity
from projects.models import Project
from notification_system.models import Notification

User = get_user_model()


@login_required
def task_list(request):
    """Display all tasks for the current user in a Kanban board format"""
    # Get user's projects
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    # Get tasks from user's projects
    tasks = Task.objects.filter(
        Q(project__in=user_projects) | Q(assigned_to=request.user)
    ).distinct().select_related('project', 'created_by').prefetch_related('assigned_to')
    
    # Organize tasks by status
    task_columns = {
        'todo': tasks.filter(status='todo'),
        'in_progress': tasks.filter(status='in_progress'),
        'review': tasks.filter(status='review'),
        'completed': tasks.filter(status='completed'),
    }
    
    # Get task statistics
    task_stats = {
        'total': tasks.count(),
        'todo': task_columns['todo'].count(),
        'in_progress': task_columns['in_progress'].count(),
        'review': task_columns['review'].count(),
        'completed': task_columns['completed'].count(),
    }
    
    context = {
        'task_columns': task_columns,
        'task_stats': task_stats,
        'projects': user_projects,
    }
    
    return render(request, 'tasks/task_list.html', context)


@login_required
def my_tasks(request):
    """Display tasks assigned to the current user"""
    # Get tasks assigned to the current user
    my_tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('project', 'created_by').prefetch_related('assigned_to')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter and status_filter in ['todo', 'in_progress', 'review', 'completed']:
        my_tasks = my_tasks.filter(status=status_filter)
    
    # Filter by project if requested
    project_filter = request.GET.get('project')
    if project_filter:
        my_tasks = my_tasks.filter(project__id=project_filter)
    
    # Filter by priority if requested
    priority_filter = request.GET.get('priority')
    if priority_filter and priority_filter in ['low', 'medium', 'high', 'urgent']:
        my_tasks = my_tasks.filter(priority=priority_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        my_tasks = my_tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Organize tasks by status for Kanban view
    task_columns = {
        'todo': my_tasks.filter(status='todo'),
        'in_progress': my_tasks.filter(status='in_progress'),
        'review': my_tasks.filter(status='review'),
        'completed': my_tasks.filter(status='completed'),
    }
    
    # Get user's projects for filtering
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    # Pagination for list view
    paginator = Paginator(my_tasks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'task_columns': task_columns,
        'my_tasks': my_tasks,
        'page_obj': page_obj,
        'projects': user_projects,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }
    
    return render(request, 'tasks/my_tasks.html', context)


@login_required
def project_tasks(request, project_id):
    """Display tasks for a specific project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if not (project.owner == request.user or request.user in project.members.all()):
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    # Get tasks for this project
    tasks = Task.objects.filter(project=project).select_related('created_by').prefetch_related('assigned_to')
    
    # Organize tasks by status
    task_columns = {
        'todo': tasks.filter(status='todo'),
        'in_progress': tasks.filter(status='in_progress'),
        'review': tasks.filter(status='review'),
        'completed': tasks.filter(status='completed'),
    }
    
    # Get project statistics
    project_stats = {
        'total_tasks': tasks.count(),
        'completed_tasks': task_columns['completed'].count(),
        'progress_percentage': (task_columns['completed'].count() / tasks.count() * 100) if tasks.count() > 0 else 0,
    }
    
    context = {
        'project': project,
        'task_columns': task_columns,
        'project_stats': project_stats,
    }
    
    return render(request, 'tasks/project_tasks.html', context)


@login_required
def task_detail(request, task_id):
    """Display detailed view of a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has access to this task
    project = task.project
    if not (project.owner == request.user or request.user in project.members.all() or request.user in task.assigned_to.all()):
        messages.error(request, 'You do not have access to this task.')
        return redirect('tasks:task_list')
    
    # Get task comments and activities
    comments = TaskComment.objects.filter(task=task).select_related('author')
    activities = TaskActivity.objects.filter(task=task).select_related('user')
    
    context = {
        'task': task,
        'comments': comments,
        'activities': activities,
    }
    
    return render(request, 'tasks/task_detail.html', context)


@login_required
@require_POST
def toggle_task_completion(request, task_id):
    """Toggle task completion status"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to update this task
    project = task.project
    if not (project.owner == request.user or request.user in project.members.all() or request.user in task.assigned_to.all()):
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    # Toggle between completed and the previous status
    if task.status == 'completed':
        # Reopen task - set to 'in_progress' by default
        new_status = 'in_progress'
        task.completed_date = None
        action = 'reopened'
    else:
        # Complete task
        new_status = 'completed'
        task.completed_date = timezone.now()
        action = 'completed'
    
    old_status = task.status
    task.status = new_status
    task.save()
    
    # Log activity
    TaskActivity.objects.create(
        task=task,
        user=request.user,
        activity_type='status_changed',
        description=f'Task {action}',
        old_value=old_status,
        new_value=new_status
    )
    
    # Create notification for assigned users
    for user in task.assigned_to.all():
        if user != request.user:
            Notification.objects.create(
                recipient=user,
                sender=request.user,
                title=f'Task {action}',
                message=f'Task "{task.title}" has been {action} by {request.user.get_full_name() or request.user.username}',
                notification_type='task_updated',
                task=task,
                project=task.project
            )
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'action': action,
        'completed_date': task.completed_date.isoformat() if task.completed_date else None
    })


@login_required
@require_POST
def update_task_status(request, task_id):
    """Update task status via AJAX"""
    task = get_object_or_404(Task, id=task_id)
    new_status = request.POST.get('status')
    
    # Validate new status
    valid_statuses = ['todo', 'in_progress', 'review', 'completed']
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status'})
    
    # Check if user has permission to update this task
    project = task.project
    if not (project.owner == request.user or request.user in project.members.all() or request.user in task.assigned_to.all()):
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    old_status = task.status
    task.status = new_status
    
    # Handle completion date
    if new_status == 'completed':
        task.completed_date = timezone.now()
    else:
        task.completed_date = None
    
    task.save()
    
    # Log activity
    TaskActivity.objects.create(
        task=task,
        user=request.user,
        activity_type='status_changed',
        description=f'Status changed from {old_status} to {new_status}',
        old_value=old_status,
        new_value=new_status
    )
    
    # Create notification for assigned users
    for user in task.assigned_to.all():
        if user != request.user:
            Notification.objects.create(
                recipient=user,
                sender=request.user,
                title='Task Status Updated',
                message=f'Task "{task.title}" status changed to {new_status.replace("_", " ").title()}',
                notification_type='task_updated',
                task=task,
                project=task.project
            )
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'old_status': old_status,
        'completed_date': task.completed_date.isoformat() if task.completed_date else None
    })


@login_required
def create_task(request):
    """Create a new task"""
    # Get user's projects with their members
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().prefetch_related('members')
    
    # Get all users who are part of user's projects for assignment
    project_members = User.objects.filter(
        Q(owned_projects__in=user_projects) |
        Q(projects__in=user_projects)
    ).distinct()
    
    if request.method == 'POST':
        # Handle task creation
        project_id = request.POST.get('project')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        assigned_to_ids = request.POST.getlist('assigned_to')
        due_date = request.POST.get('due_date')
        
        # Validate required fields
        if not title or not project_id:
            messages.error(request, 'Title and Project are required.')
            context = {
                'projects': user_projects,
                'project_members': project_members
            }
            return render(request, 'tasks/create_task.html', context)
        
        # Get project and validate access
        try:
            project = Project.objects.get(id=project_id)
            if not (project.owner == request.user or request.user in project.members.all()):
                messages.error(request, 'You do not have access to this project.')
                return redirect('tasks:task_list')
        except Project.DoesNotExist:
            messages.error(request, 'Invalid project selected.')
            context = {
                'projects': user_projects,
                'project_members': project_members
            }
            return render(request, 'tasks/create_task.html', context)
        
        # Create task
        task = Task.objects.create(
            project=project,
            title=title,
            description=description,
            priority=priority,
            created_by=request.user,
            due_date=due_date if due_date else None
        )
        
        # Assign users
        if assigned_to_ids:
            task.assigned_to.set(assigned_to_ids)
        
        # Log activity
        TaskActivity.objects.create(
            task=task,
            user=request.user,
            activity_type='created',
            description=f'Task created'
        )
        
        # Create notifications for assigned users
        for user_id in assigned_to_ids:
            try:
                user = User.objects.get(id=user_id)
                if user != request.user:
                    Notification.objects.create(
                        recipient=user,
                        sender=request.user,
                        title='New Task Assigned',
                        message=f'You have been assigned to task "{task.title}"',
                        notification_type='task_assigned',
                        task=task,
                        project=project
                    )
            except User.DoesNotExist:
                pass
        
        messages.success(request, 'Task created successfully!')
        return redirect('tasks:task_detail', task_id=task.id)
    
    context = {
        'projects': user_projects,
        'project_members': project_members
    }
    return render(request, 'tasks/create_task.html', context)


@login_required
def edit_task(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to edit this task
    project = task.project
    if not (project.owner == request.user or request.user in project.members.all()):
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('tasks:task_detail', task_id=task.id)
    
    # Get user's projects
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    if request.method == 'POST':
        # Handle task update
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        assigned_to_ids = request.POST.getlist('assigned_to')
        due_date = request.POST.get('due_date')
        
        # Update task fields
        old_values = {
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'due_date': task.due_date,
        }
        
        task.title = title
        task.description = description
        task.priority = priority
        
        # Handle status change
        if status != task.status:
            task.status = status
            if status == 'completed':
                task.completed_date = timezone.now()
            else:
                task.completed_date = None
        
        task.due_date = due_date if due_date else None
        task.save()
        
        # Update assigned users
        task.assigned_to.set(assigned_to_ids)
        
        # Log activity for significant changes
        changes = []
        if old_values['title'] != task.title:
            changes.append(f"Title: '{old_values['title']}' → '{task.title}'")
        if old_values['priority'] != task.priority:
            changes.append(f"Priority: {old_values['priority']} → {task.priority}")
        if old_values['status'] != task.status:
            changes.append(f"Status: {old_values['status']} → {task.status}")
        
        if changes:
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                activity_type='updated',
                description=f'Task updated: {", ".join(changes)}'
            )
        
        messages.success(request, 'Task updated successfully!')
        return redirect('tasks:task_detail', task_id=task.id)
    
    context = {
        'task': task,
        'projects': user_projects,
    }
    return render(request, 'tasks/edit_task.html', context)


@login_required
@require_POST
def delete_task(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to delete this task
    project = task.project
    if not (project.owner == request.user or task.created_by == request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    task_title = task.title
    project_id = task.project.id
    task.delete()
    
    messages.success(request, f'Task "{task_title}" deleted successfully!')
    return JsonResponse({'success': True, 'redirect_url': f'/tasks/project/{project_id}/'})
