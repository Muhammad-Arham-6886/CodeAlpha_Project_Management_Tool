import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from projects.models import Project
from django.db import connection

def debug_project_deletion():
    # Get the project that's causing issues
    project_id = "230d90f6-6d73-4e57-88f9-0220bf244cfd"
    try:
        project = Project.objects.get(id=project_id)
        print(f"Found project: {project.name}")
        
        # Check what tables reference this project
        with connection.cursor() as cursor:
            project_id_str = str(project.id).replace('-', '')
            print(f"Project ID without hyphens: {project_id_str}")
            
            # Check what's referencing this project
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND sql LIKE '%project_id%'")
            tables = cursor.fetchall()
            print("Tables with project_id:", tables)
            
            # Check specific references
            tables_to_check = [
                'tasks_task',
                'tasks_tasklist', 
                'task_management_task',
                'notification_system_notification',
                'projects_projectinvitation',
                'projects_projectmembership'
            ]
            
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id = %s", [project_id_str])
                    count = cursor.fetchone()[0]
                    print(f"{table}: {count} references")
                except Exception as e:
                    print(f"Error checking {table}: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")

def test_project_deletion():
    # Get the project that's causing issues
    project_id = "230d90f6-6d73-4e57-88f9-0220bf244cfd"
    try:
        project = Project.objects.get(id=project_id)
        print(f"Found project: {project.name}")
        
        # Test the deletion logic
        from django.db import transaction
        
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
                
                # 3. Delete project memberships
                try:
                    cursor.execute("DELETE FROM projects_projectmembership WHERE project_id = %s", [project_id_str])
                    print(f"Deleted memberships: {cursor.rowcount} rows")
                except Exception as e:
                    print(f"Error deleting memberships: {e}")
                    raise
                
                # 4. Finally delete the project itself
                cursor.execute("DELETE FROM projects_project WHERE id = %s", [project_id_str])
                print(f"Deleted project: {cursor.rowcount} rows")
                
        print("Project deletion test completed successfully!")
        
    except Exception as e:
        print(f"Error during deletion test: {e}")
        import traceback
        traceback.print_exc()
    # Get the project that's causing issues
    project_id = "230d90f6-6d73-4e57-88f9-0220bf244cfd"
    try:
        project = Project.objects.get(id=project_id)
        print(f"Found project: {project.name}")
        
        # Test the deletion logic
        from django.db import transaction
        
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
                
                # 3. Delete project memberships
                try:
                    cursor.execute("DELETE FROM projects_projectmembership WHERE project_id = %s", [project_id_str])
                    print(f"Deleted memberships: {cursor.rowcount} rows")
                except Exception as e:
                    print(f"Error deleting memberships: {e}")
                    raise
                
                # 4. Finally delete the project itself
                cursor.execute("DELETE FROM projects_project WHERE id = %s", [project_id_str])
                print(f"Deleted project: {cursor.rowcount} rows")
                
        print("Project deletion test completed successfully!")
        
    except Exception as e:
        print(f"Error during deletion test: {e}")
        import traceback
        traceback.print_exc()
    # Get the project that's causing issues
    project_id = "230d90f6-6d73-4e57-88f9-0220bf244cfd"
    try:
        project = Project.objects.get(id=project_id)
        print(f"Found project: {project.name}")
        
        # Check what tables reference this project
        with connection.cursor() as cursor:
            project_id_str = str(project.id).replace('-', '')
            print(f"Project ID without hyphens: {project_id_str}")
            
            # Check what's referencing this project
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND sql LIKE '%project_id%'")
            tables = cursor.fetchall()
            print("Tables with project_id:", tables)
            
            # Check specific references
            tables_to_check = [
                'tasks_task',
                'tasks_tasklist', 
                'task_management_task',
                'notification_system_notification',
                'projects_projectinvitation',
                'projects_projectmembership'
            ]
            
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id = %s", [project_id_str])
                    count = cursor.fetchone()[0]
                    print(f"{table}: {count} references")
                except Exception as e:
                    print(f"Error checking {table}: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_project_deletion()
    print("\n" + "="*50 + "\n")
    test_project_deletion()
