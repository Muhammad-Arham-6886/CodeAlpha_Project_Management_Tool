from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from projects.models import Project
from django.db.models import Q

@login_required
def get_project_members(request, project_id):
    """Get members of a specific project via AJAX"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if not (project.owner == request.user or request.user in project.members.all()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get project members
    members = []
    
    # Add project owner
    members.append({
        'id': project.owner.id,
        'name': project.owner.get_full_name() or project.owner.username,
        'username': project.owner.username,
        'is_owner': True
    })
    
    # Add project members
    for member in project.members.all():
        if member != project.owner:  # Avoid duplicates
            members.append({
                'id': member.id,
                'name': member.get_full_name() or member.username,
                'username': member.username,
                'is_owner': False
            })
    
    return JsonResponse({'members': members})
