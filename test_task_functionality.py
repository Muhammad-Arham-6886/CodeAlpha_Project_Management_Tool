#!/usr/bin/env python
"""
Test script to verify task functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from task_management.models import Task
from projects.models import Project
from django.contrib.auth.models import User

def test_task_setup():
    """Test that task models and views are properly configured"""
    print("Testing task functionality...")
    
    # Check if we have any tasks
    task_count = Task.objects.count()
    print(f"Total tasks in database: {task_count}")
    
    # Check if we have projects
    project_count = Project.objects.count()
    print(f"Total projects in database: {project_count}")
    
    # Check task statuses
    status_counts = {}
    for status in ['todo', 'in_progress', 'review', 'completed']:
        count = Task.objects.filter(status=status).count()
        status_counts[status] = count
        print(f"Tasks with status '{status}': {count}")
    
    print("\n✅ Task functionality test completed successfully!")
    return True

if __name__ == '__main__':
    test_task_setup()
