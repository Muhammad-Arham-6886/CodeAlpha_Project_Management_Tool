from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Project, ProjectMembership

User = get_user_model()

# Safe imports for optional apps
try:
    from tasks.models import Task
except ImportError:
    Task = None

try:
    from notifications.models import Notification
except ImportError:
    Notification = None

@login_required
def dashboard(request):
    """Main dashboard view with real data"""
    # Get user's projects
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-updated_at')[:5]
    
    total_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().count()
    
    # Calculate task statistics if Task model exists
    active_tasks = 0
    pending_tasks = 0
    overdue_tasks = 0
    user_tasks = []
    
    if Task:
        user_tasks_queryset = Task.objects.filter(
            Q(assigned_to=request.user) | Q(project__owner=request.user) | Q(project__members=request.user)
        ).distinct()
        
        pending_tasks = user_tasks_queryset.filter(status__in=['todo', 'in_progress']).count()
        overdue_tasks = user_tasks_queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()
        active_tasks = user_tasks_queryset.filter(status__in=['todo', 'in_progress']).count()
        user_tasks = user_tasks_queryset.order_by('-updated_at')[:5]
    
    context = {
        'recent_projects': user_projects,
        'recent_tasks': user_tasks,
        'total_projects': total_projects,
        'active_tasks': active_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_activities': [],
    }
    return render(request, 'projects/dashboard.html', context)

@login_required
def project_list(request):
    """Project list view with search and filtering"""
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-updated_at')
    
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
    
    # Add task statistics to each project
    for project in projects:
        project.total_tasks = 0
        project.completed_tasks = 0
        project.progress_percentage = 0
        
        if Task:
            tasks = Task.objects.filter(project=project)
            project.total_tasks = tasks.count()
            project.completed_tasks = tasks.filter(status='completed').count()
            if project.total_tasks > 0:
                project.progress_percentage = int((project.completed_tasks / project.total_tasks) * 100)
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search,
        'status_filter': status,
    }
    return render(request, 'projects/project_list.html', context)

@login_required
def create_project(request):
    """Create project view with full form handling"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'planning')
        priority = request.POST.get('priority', 'medium')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        budget = request.POST.get('budget', '')
        color = request.POST.get('color', '#667eea')
        
        if not name:
            messages.error(request, 'Project name is required.')
            return render(request, 'projects/create_project.html', {
                'form_data': request.POST,
                'title': 'Create New Project'
            })
        
        try:
            # Create the project
            project = Project.objects.create(
                name=name,
                description=description,
                status=status,
                priority=priority,
                owner=request.user,
                color=color
            )
            
            # Handle dates
            if start_date:
                project.start_date = start_date
            if end_date:
                project.end_date = end_date
            if budget:
                try:
                    project.budget = float(budget)
                except ValueError:
                    pass
            
            project.save()
            
            # Add owner as admin member
            ProjectMembership.objects.create(
                project=project,
                user=request.user,
                role='admin'
            )
            
            messages.success(request, f'Project "{name}" created successfully!')
            return redirect('projects:project_detail', project_id=project.id)
            
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
    
    context = {'title': 'Create New Project'}
    return render(request, 'projects/create_project.html', context)

@login_required
def project_detail(request, project_id):
    """Project detail view with member management"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check access permissions
    if not (project.owner == request.user or project.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have permission to view this project.")
        return redirect('projects:project_list')
    
    # Get project members
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')
    
    # Calculate task statistics
    task_stats = {
        'total': 0,
        'completed': 0,
        'in_progress': 0,
        'todo': 0,
        'review': 0,
    }
    
    if Task:
        tasks = Task.objects.filter(project=project)
        task_stats = {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'todo': tasks.filter(status='todo').count(),
            'review': tasks.filter(status='review').count(),
        }
    
    # Handle member invitation
    if request.method == 'POST' and 'invite_email' in request.POST:
        if project.owner == request.user:
            email = request.POST.get('invite_email', '').strip()
            role = request.POST.get('invite_role', 'member')
            
            if email:
                try:
                    user = User.objects.get(email=email)
                    if not ProjectMembership.objects.filter(project=project, user=user).exists():
                        ProjectMembership.objects.create(
                            project=project,
                            user=user,
                            role=role
                        )
                        messages.success(request, f'{email} has been added to the project.')
                    else:
                        messages.warning(request, f'{email} is already a member of this project.')
                except User.DoesNotExist:
                    messages.error(request, f'No user found with email: {email}')
            else:
                messages.error(request, 'Email is required.')
        else:
            messages.error(request, 'Only project owners can invite members.')
        
        return redirect('projects:project_detail', project_id=project.id)
    
    context = {
        'project': project,
        'memberships': memberships,
        'task_stats': task_stats,
        'can_edit': project.owner == request.user,
        'can_invite': project.owner == request.user,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def edit_project(request, project_id):
    """Edit project view with validation"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    user_membership = ProjectMembership.objects.filter(
        project=project, user=request.user
    ).first()
    
    if not (project.owner == request.user or 
            (user_membership and user_membership.role in ['admin', 'manager'])):
        messages.error(request, "You don't have permission to edit this project.")
        return redirect('projects:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', project.status)
        priority = request.POST.get('priority', project.priority)
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        budget = request.POST.get('budget', '')
        color = request.POST.get('color', project.color)
        
        if not name:
            messages.error(request, 'Project name is required.')
        else:
            try:
                project.name = name
                project.description = description
                project.status = status
                project.priority = priority
                project.color = color
                
                # Handle dates
                if start_date:
                    project.start_date = start_date
                if end_date:
                    project.end_date = end_date
                if budget:
                    try:
                        project.budget = float(budget)
                    except ValueError:
                        pass
                
                project.save()
                messages.success(request, f'Project "{name}" updated successfully!')
                return redirect('projects:project_detail', project_id=project.id)
                
            except Exception as e:
                messages.error(request, f'Error updating project: {str(e)}')
    
    context = {
        'project': project,
        'title': f'Edit {project.name}'
    }
    return render(request, 'projects/edit_project.html', context)

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
        project.delete()
        messages.success(request, f'Project "{project_name}" has been deleted successfully.')
        return redirect('projects:project_list')
    
    context = {'project': project}
    return render(request, 'projects/delete_project.html', context)

@login_required
def project_members(request, project_id):
    """Project members management view"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check access permissions
    if not (project.owner == request.user or project.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have permission to view this project.")
        return redirect('projects:project_list')
    
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')
    
    context = {
        'project': project,
        'memberships': memberships,
        'can_manage': project.owner == request.user,
    }
    return render(request, 'projects/project_members.html', context)

@login_required
def invite_member(request, project_id):
    """AJAX view for inviting team members"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    if project.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    email = request.POST.get('email', '').strip()
    role = request.POST.get('role', 'member')
    
    if not email:
        return JsonResponse({'success': False, 'error': 'Email is required'})
    
    try:
        user = User.objects.get(email=email)
        
        # Check if already a member
        if ProjectMembership.objects.filter(project=project, user=user).exists():
            return JsonResponse({'success': False, 'error': f'{email} is already a member'})
        
        # Create membership
        membership = ProjectMembership.objects.create(
            project=project,
            user=user,
            role=role
        )
        
        # Create notification if available
        if Notification:
            Notification.objects.create(
                recipient=user,
                title=f'Invited to {project.name}',
                message=f'You have been invited to join the project "{project.name}" as a {role}.',
                notification_type='project_invitation',
                project=project
            )
        
        return JsonResponse({
            'success': True, 
            'message': f'{email} has been invited to the project',
            'member': {
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'role': role,
                'joined': membership.joined_at.strftime('%B %d, %Y')
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'No user found with email: {email}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def project_board(request, project_id):
    """Kanban board view with task management"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check access permissions
    if not (project.owner == request.user or project.members.filter(id=request.user.id).exists()):
        messages.error(request, "You don't have permission to view this project.")
        return redirect('projects:project_list')
    
    # Get project members for task assignment
    project_members = ProjectMembership.objects.filter(project=project).select_related('user')
    
    # Initialize task lists
    todo_tasks = []
    in_progress_tasks = []
    review_tasks = []
    completed_tasks = []
    
    # Get tasks if Task model is available
    if Task:
        tasks = Task.objects.filter(project=project).select_related('created_by').prefetch_related('assigned_to')
        
        todo_tasks = tasks.filter(status='todo')
        in_progress_tasks = tasks.filter(status='in_progress')
        review_tasks = tasks.filter(status='review')
        completed_tasks = tasks.filter(status='completed')
    
    # Handle AJAX task creation
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if Task:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            status = request.POST.get('status', 'todo')
            priority = request.POST.get('priority', 'medium')
            assignee_id = request.POST.get('assignee_id')
            
            if title:
                try:
                    task = Task.objects.create(
                        project=project,
                        title=title,
                        description=description,
                        status=status,
                        priority=priority,
                        created_by=request.user
                    )
                    
                    if assignee_id:
                        try:
                            assignee = User.objects.get(id=assignee_id)
                            task.assigned_to.add(assignee)
                        except User.DoesNotExist:
                            pass
                    
                    return JsonResponse({
                        'success': True,
                        'task': {
                            'id': str(task.id),
                            'title': task.title,
                            'description': task.description,
                            'status': task.status,
                            'priority': task.priority,
                            'created_by': task.created_by.get_full_name() or task.created_by.username,
                            'assigned_to': [u.get_full_name() or u.username for u in task.assigned_to.all()],
                        }
                    })
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': 'Title is required'})
        else:
            return JsonResponse({'success': False, 'error': 'Task model not available'})
    
    context = {
        'project': project,
        'project_members': project_members,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'completed_tasks': completed_tasks,
        'can_manage_tasks': True,  # All project members can manage tasks
    }
    return render(request, 'projects/project_board.html', context)
