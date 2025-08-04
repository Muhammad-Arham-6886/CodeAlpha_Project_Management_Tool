from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Project, ProjectMembership
from .forms import ProjectForm, InviteTeamMemberForm
from .safe_delete import safe_delete_project

# Safe imports for optional apps
try:
    from task_management.models import Task
except ImportError:
    Task = None

try:
    from notification_system.models import Notification
except ImportError:
    Notification = None


# Helper: calculate project task stats
def get_task_stats(tasks_queryset):
    return {
        'total': tasks_queryset.count(),
        'completed': tasks_queryset.filter(status='completed').count(),
        'in_progress': tasks_queryset.filter(status='in_progress').count(),
        'todo': tasks_queryset.filter(status='todo').count(),
        'review': tasks_queryset.filter(status='review').count() if hasattr(tasks_queryset, 'filter') else 0,
    }


@login_required
def dashboard(request):
    """Main dashboard view"""
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-updated_at')[:5]
    
    total_projects = user_projects.count()
    user_tasks = []
    pending_tasks = overdue_tasks = active_tasks = 0

    if Task:
        user_tasks_queryset = Task.objects.filter(
            Q(assigned_to=request.user) | 
            Q(project__owner=request.user) | 
            Q(project__members=request.user)
        ).distinct()

        pending_tasks = user_tasks_queryset.filter(status='todo').count()
        active_tasks = user_tasks_queryset.filter(status__in=['todo', 'in_progress']).count()
        overdue_tasks = user_tasks_queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()

        user_tasks = user_tasks_queryset.order_by('-updated_at')[:5]

    context = {
        'recent_projects': user_projects,
        'recent_tasks': user_tasks,
        'total_projects': total_projects,
        'active_tasks': active_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_activities': [],  # Placeholder for future implementation
    }
    return render(request, 'projects/dashboard.html', context)


@login_required
def project_list(request):
    """View for listing all user's projects"""
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()

    # Search & filter
    search = request.GET.get('search')
    if search:
        projects = projects.filter(Q(name__icontains=search) | Q(description__icontains=search))

    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)

    projects = projects.order_by('-updated_at')

    # Add progress stats
    if Task:
        for project in projects:
            tasks = Task.objects.filter(project=project)
            stats = get_task_stats(tasks)
            project.total_tasks = stats['total']
            project.completed_tasks = stats['completed']
            project.progress_percentage = int((stats['completed'] / stats['total']) * 100) if stats['total'] > 0 else 0
    else:
        for project in projects:
            project.total_tasks = 0
            project.completed_tasks = 0
            project.progress_percentage = 0

    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'projects/project_list.html', {
        'projects': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })


@login_required
def project_detail(request, project_id):
    """View for project details and team management"""
    project = get_object_or_404(Project, id=project_id)

    if not (project.owner == request.user or request.user in project.members.all()):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:project_list')

    memberships = ProjectMembership.objects.filter(project=project)
    task_stats = {'total': 0, 'completed': 0, 'in_progress': 0, 'todo': 0}

    if Task:
        tasks = Task.objects.filter(project=project)
        task_stats = get_task_stats(tasks)

    if request.method == 'POST':
        form = InviteTeamMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['email']  # Ensure form returns a User
            role = form.cleaned_data['role']

            if ProjectMembership.objects.filter(project=project, user=user).exists():
                messages.warning(request, f"{user.email} is already a member of this project.")
            else:
                ProjectMembership.objects.create(project=project, user=user, role=role)

                if Notification:
                    Notification.objects.create(
                        recipient=user,
                        title=f'Invited to {project.name}',
                        message=f'You have been invited to join the project "{project.name}" as a {role}.',
                        notification_type='project_invite',
                        project=project
                    )
                messages.success(request, f"{user.email} has been invited to the project.")
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = InviteTeamMemberForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'memberships': memberships,
        'form': form,
        'task_stats': task_stats,
    })


@login_required
def create_project(request):
    """View for creating a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            
            # Add the owner as a project member with admin role
            ProjectMembership.objects.create(
                project=project,
                user=request.user,
                role='admin'
            )
            
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('projects:project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create_project.html', {'form': form})


@login_required
def edit_project(request, project_id):
    """View for editing an existing project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to edit this project
    if not (project.owner == request.user or 
            ProjectMembership.objects.filter(project=project, user=request.user, role__in=['admin', 'manager']).exists()):
        messages.error(request, "You don't have permission to edit this project.")
        return redirect('projects:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'is_edit': True,
    }
    
    return render(request, 'projects/edit_project.html', context)


@login_required
def delete_project(request, project_id):
    """Delete project view with confirmation"""
    project = get_object_or_404(Project, id=project_id)
    
    # Only project owner can delete
    if project.owner != request.user:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': 'Only the project owner can delete this project.'})
        messages.error(request, "Only the project owner can delete this project.")
        return redirect('projects:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        project_name = project.name
        try:
            success, message = safe_delete_project(project)
            if success:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'success': True, 'message': message})
                messages.success(request, f'Project "{project_name}" has been deleted successfully.')
                return redirect('projects:project_list')
            else:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'success': False, 'error': message})
                messages.error(request, f'Error deleting project: {message}')
                return redirect('projects:project_detail', project_id=project.id)
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error deleting project: {str(e)}. Please try again.')
            return redirect('projects:project_detail', project_id=project.id)
    
    context = {'project': project}
    return render(request, 'projects/delete_project.html', context)


@login_required
def project_members(request, project_id):
    """Project members management view"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if not (project.owner == request.user or request.user in project.members.all()):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:project_list')
    
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')
    
    context = {
        'project': project,
        'memberships': memberships,
    }
    
    return render(request, 'projects/project_members.html', context)


@login_required
def invite_member(request, project_id):
    """AJAX view for inviting team members"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to invite members
    if not (project.owner == request.user or 
            ProjectMembership.objects.filter(project=project, user=request.user, role__in=['admin', 'manager']).exists()):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'})
    
    if request.method == 'POST':
        form = InviteTeamMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['email']
            role = form.cleaned_data['role']
            
            # Check if user is already a member
            if ProjectMembership.objects.filter(project=project, user=user).exists():
                return JsonResponse({'status': 'error', 'message': f'{user.email} is already a member'})
            
            # Create membership
            membership = ProjectMembership.objects.create(
                project=project,
                user=user,
                role=role
            )
            
            # Create notification for the invited user
            if Notification:
                Notification.objects.create(
                    recipient=user,
                    title=f'Invited to {project.name}',
                    message=f'You have been invited to join the project "{project.name}" as a {role}.',
                    notification_type='project_invite',
                    project=project
                )
            
            return JsonResponse({
                'status': 'success', 
                'message': f'{user.email} has been invited to the project',
                'member': {
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                    'role': role,
                    'joined': membership.joined_at.strftime('%B %d, %Y')
                }
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def project_board(request, project_id):
    """View for project Kanban board"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if not (project.owner == request.user or request.user in project.members.all()):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:project_list')
    
    # Initialize empty task lists
    todo_tasks = []
    in_progress_tasks = []
    review_tasks = []
    completed_tasks = []
    
    # Get tasks organized by status if Task model is available
    if Task:
        tasks = Task.objects.filter(project=project).select_related('assigned_to', 'project')
        
        todo_tasks = tasks.filter(status='todo')
        in_progress_tasks = tasks.filter(status='in_progress')
        review_tasks = tasks.filter(status='review')
        completed_tasks = tasks.filter(status='completed')
    
    context = {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'completed_tasks': completed_tasks,
    }
    
    return render(request, 'projects/project_board.html', context)
