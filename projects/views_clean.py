from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Project, ProjectMembership
from .forms import ProjectForm, InviteTeamMemberForm
from .safe_delete import safe_delete_project

# Safe imports for optional apps
try:
    from task_management.models import Task, TaskComment, TaskAttachment, TaskActivity
except ImportError:
    Task = None
    TaskComment = None
    TaskAttachment = None
    TaskActivity = None

try:
    from notification_system.models import Notification
except ImportError:
    Notification = None


@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get user's projects
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-updated_at')[:5]
    
    # Initialize basic stats
    total_projects = user_projects.count()
    active_tasks = 0
    pending_tasks = 0
    overdue_tasks = 0
    user_tasks = []
    
    # Only query tasks if Task model is available
    if Task:
        user_tasks_queryset = Task.objects.filter(
            Q(assigned_to=request.user) | Q(project__owner=request.user) | Q(project__members=request.user)
        ).distinct()
        
        # Calculate statistics before slicing
        pending_tasks = user_tasks_queryset.filter(
            status__in=['todo', 'in_progress']
        ).count()
        overdue_tasks = user_tasks_queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()
        active_tasks = user_tasks_queryset.filter(
            status__in=['todo', 'in_progress']
        ).count()
        
        # Get recent tasks for display (slice after stats calculation)
        user_tasks = user_tasks_queryset.order_by('-updated_at')[:5]
    
    context = {
        'recent_projects': user_projects,
        'recent_tasks': user_tasks,
        'total_projects': total_projects,
        'active_tasks': active_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_activities': [],  # Will implement later
    }
    
    return render(request, 'projects/dashboard.html', context)

@login_required
def project_list(request):
    """View for listing all user's projects"""
    # Get user's projects
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        projects = projects.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    # Order projects
    projects = projects.order_by('-updated_at')
    
    # Add calculated stats to each project if tasks are available
    for project in projects:
        if hasattr(project, 'tasks'):
            project.total_tasks = project.tasks.count()
            project.completed_tasks = project.tasks.filter(status='completed').count()
            project.progress_percentage = int((project.completed_tasks / project.total_tasks * 100)) if project.total_tasks > 0 else 0
        else:
            project.total_tasks = 0
            project.completed_tasks = 0
            project.progress_percentage = 0
    
    # Pagination
    paginator = Paginator(projects, 12)  # Show 12 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'projects/project_list.html', context)

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
def project_detail(request, project_id):
    """View for project details and team management"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if not (project.owner == request.user or request.user in project.members.all()):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:project_list')
    
    # Get project members
    memberships = ProjectMembership.objects.filter(project=project)
    
    # Get project tasks
    task_stats = {
        'total': 0,
        'completed': 0,
        'in_progress': 0,
        'todo': 0,
    }
    
    # Only calculate task stats if tasks are available
    if hasattr(project, 'tasks'):
        tasks = project.tasks.all()
        task_stats = {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'todo': tasks.filter(status='todo').count(),
        }
    
    # Handle team invitation
    if request.method == 'POST':
        form = InviteTeamMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['email']  # This returns the User object
            role = form.cleaned_data['role']
            
            # Check if user is already a member
            if ProjectMembership.objects.filter(project=project, user=user).exists():
                messages.warning(request, f"{user.email} is already a member of this project.")
            else:
                ProjectMembership.objects.create(
                    project=project,
                    user=user,
                    role=role
                )
                
                # Create notification
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
    
    context = {
        'project': project,
        'memberships': memberships,
        'form': form,
        'task_stats': task_stats,
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def delete_project(request, project_id):
    """Delete project view with confirmation"""
    project = get_object_or_404(Project, id=project_id)
    
    # Only project owner can delete
    if project.owner != request.user:
        messages.error(request, "Only the project owner can delete this project.")
        return redirect('projects:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        project_name = project.name
        try:
            safe_delete_project(project)
            messages.success(request, f'Project "{project_name}" has been deleted successfully.')
            return redirect('projects:project_list')
        except Exception as e:
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
    if hasattr(project, 'tasks'):
        tasks = project.tasks.all().select_related('assigned_to', 'project')
        
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
