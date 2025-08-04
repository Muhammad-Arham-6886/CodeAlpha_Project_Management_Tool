@login_required
def delete_project(request, project_id):
    """View for deleting a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Only project owner can delete the project
    if project.owner != request.user:
        messages.error(request, "Only the project owner can delete this project.")
        return redirect('projects:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        project_name = project.name
        
        try:
            from django.db import transaction, connection
            
            with transaction.atomic():
                with connection.cursor() as cursor:
                    project_id_str = str(project.id).replace('-', '')
                    print(f"Project ID without hyphens: {project_id_str}")
                    
                    # 1. Delete from tasks_task table and all related objects
                    try:
                        # First, get all task IDs from this project
                        cursor.execute("SELECT id FROM tasks_task WHERE project_id = %s", [project_id_str])
                        task_ids = [row[0] for row in cursor.fetchall()]
                        
                        if task_ids:
                            print(f"Found {len(task_ids)} tasks in tasks_task")
                            
                            # For each task, delete all related objects
                            for task_id in task_ids:
                                # Delete task comments (including child comments)
                                cursor.execute("DELETE FROM tasks_taskcomment WHERE task_id = %s OR parent_comment_id IN (SELECT id FROM tasks_taskcomment WHERE task_id = %s)", [task_id, task_id])
                                
                                # Delete task activities
                                cursor.execute("DELETE FROM tasks_taskactivity WHERE task_id = %s", [task_id])
                                
                                # Delete task attachments
                                cursor.execute("DELETE FROM tasks_taskattachment WHERE task_id = %s", [task_id])
                                
                                # Delete task assigned_to relationships (M2M)
                                cursor.execute("DELETE FROM tasks_task_assigned_to WHERE task_id = %s", [task_id])
                                
                                # Delete task tags relationships (M2M)
                                cursor.execute("DELETE FROM tasks_task_tags WHERE task_id = %s", [task_id])
                            
                            # Handle parent_task_id self-referencing foreign keys
                            # First, update any tasks that have these tasks as parents
                            for task_id in task_ids:
                                cursor.execute("UPDATE tasks_task SET parent_task_id = NULL WHERE parent_task_id = %s", [task_id])
                            
                            # Now delete all tasks
                            for task_id in task_ids:
                                cursor.execute("DELETE FROM tasks_task WHERE id = %s", [task_id])
                            
                            print(f"Deleted {len(task_ids)} tasks and related objects from tasks_task")
                        
                    except Exception as e:
                        print(f"Error deleting tasks_task objects: {e}")
                        raise
                    
                    # 2. Delete task lists from tasks_tasklist
                    try:
                        cursor.execute("DELETE FROM tasks_tasklist WHERE project_id = %s", [project_id_str])
                        print(f"Deleted from tasks_tasklist: {cursor.rowcount} rows")
                    except Exception as e:
                        print(f"Error deleting from tasks_tasklist: {e}")
                        raise
                    
                    # 3. Delete from task_management_task and related tables
                    try:
                        # First get all task IDs for this project from task_management
                        cursor.execute("SELECT id FROM task_management_task WHERE project_id = %s", [project_id_str])
                        task_ids = [row[0] for row in cursor.fetchall()]
                        
                        if task_ids:
                            # For each task, delete related objects
                            for task_id in task_ids:
                                cursor.execute("DELETE FROM task_management_taskactivity WHERE task_id = %s", [task_id])
                                cursor.execute("DELETE FROM task_management_taskcomment WHERE task_id = %s", [task_id])
                                cursor.execute("DELETE FROM task_management_taskattachment WHERE task_id = %s", [task_id])
                                cursor.execute("DELETE FROM task_management_task_assigned_to WHERE task_id = %s", [task_id])
                            print(f"Deleted task_management objects for {len(task_ids)} tasks")
                        
                        # Delete tasks themselves
                        cursor.execute("DELETE FROM task_management_task WHERE project_id = %s", [project_id_str])
                        print(f"Deleted from task_management_task: {cursor.rowcount} rows")
                        
                    except Exception as e:
                        print(f"Error deleting task_management objects: {e}")
                        raise
                    
                    # 4. Delete notifications
                    try:
                        cursor.execute("DELETE FROM notification_system_notification WHERE project_id = %s", [project_id_str])
                        print(f"Deleted notifications: {cursor.rowcount} rows")
                    except Exception as e:
                        print(f"Error deleting notifications: {e}")
                        raise
                    
                    # 5. Delete project invitations
                    try:
                        cursor.execute("DELETE FROM projects_projectinvitation WHERE project_id = %s", [project_id_str])
                        print(f"Deleted invitations: {cursor.rowcount} rows")
                    except Exception as e:
                        print(f"Error deleting invitations: {e}")
                        raise
                    
                    # 6. Delete project memberships
                    try:
                        cursor.execute("DELETE FROM projects_projectmembership WHERE project_id = %s", [project_id_str])
                        print(f"Deleted memberships: {cursor.rowcount} rows")
                    except Exception as e:
                        print(f"Error deleting memberships: {e}")
                        raise
                    
                    # 7. Finally delete the project itself
                    cursor.execute("DELETE FROM projects_project WHERE id = %s", [project_id_str])
                    print(f"Deleted project: {cursor.rowcount} rows")
                    
            messages.success(request, f'Project "{project_name}" has been deleted successfully.')
            return redirect('projects:project_list')
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Delete error: {error_details}")
            messages.error(request, f'Error deleting project: {str(e)}. Please try again.')
            return redirect('projects:project_detail', project_id=project.id)
    
    context = {
        'project': project,
    }
    
    return render(request, 'projects/delete_project.html', context)
