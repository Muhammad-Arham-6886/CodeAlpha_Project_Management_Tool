#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from accounts.models import User, UserProfile
from projects.models import Project, ProjectMembership
from tasks.models import TaskList, Task

def create_sample_data():
    print("Creating sample data...")
    
    # Create additional users
    users = []
    
    # Create team members
    if not User.objects.filter(username='john_doe').exists():
        john = User.objects.create_user(
            username='john_doe',
            email='john@example.com',
            password='demo123',
            first_name='John',
            last_name='Doe',
            bio='Frontend Developer with 5 years experience'
        )
        UserProfile.objects.create(
            user=john,
            skills='JavaScript, React, CSS, HTML',
            availability_status='available'
        )
        users.append(john)
        print(f"Created user: {john.username}")
    
    if not User.objects.filter(username='jane_smith').exists():
        jane = User.objects.create_user(
            username='jane_smith',
            email='jane@example.com',
            password='demo123',
            first_name='Jane',
            last_name='Smith',
            bio='Backend Developer and DevOps Engineer'
        )
        UserProfile.objects.create(
            user=jane,
            skills='Python, Django, Docker, AWS',
            availability_status='available'
        )
        users.append(jane)
        print(f"Created user: {jane.username}")
    
    if not User.objects.filter(username='mike_wilson').exists():
        mike = User.objects.create_user(
            username='mike_wilson',
            email='mike@example.com',
            password='demo123',
            first_name='Mike',
            last_name='Wilson',
            bio='UI/UX Designer and Product Manager'
        )
        UserProfile.objects.create(
            user=mike,
            skills='Figma, Adobe XD, Product Strategy, User Research',
            availability_status='busy'
        )
        users.append(mike)
        print(f"Created user: {mike.username}")
    
    # Get admin user
    admin = User.objects.get(username='admin')
    users.append(admin)
    
    # Create sample projects
    projects = []
    
    if not Project.objects.filter(name='E-commerce Website Redesign').exists():
        project1 = Project.objects.create(
            name='E-commerce Website Redesign',
            description='Complete redesign of the company e-commerce platform with modern UI/UX and improved performance.',
            status='active',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=90)).date(),
            owner=admin
        )
        projects.append(project1)
        print(f"Created project: {project1.name}")
    
    if not Project.objects.filter(name='Mobile App Development').exists():
        project2 = Project.objects.create(
            name='Mobile App Development',
            description='Development of cross-platform mobile application for customer engagement.',
            status='active',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=120)).date(),
            owner=admin
        )
        projects.append(project2)
        print(f"Created project: {project2.name}")
    
    if not Project.objects.filter(name='Data Analytics Dashboard').exists():
        project3 = Project.objects.create(
            name='Data Analytics Dashboard',
            description='Internal dashboard for business intelligence and data visualization.',
            status='planning',
            start_date=(datetime.now() + timedelta(days=30)).date(),
            end_date=(datetime.now() + timedelta(days=150)).date(),
            owner=admin
        )
        projects.append(project3)
        print(f"Created project: {project3.name}")
    
    # Add team members to projects
    for project in projects:
        for user in users:
            if not ProjectMembership.objects.filter(project=project, user=user).exists():
                role = 'admin' if user == admin else 'member'
                if user.username == 'mike_wilson':
                    role = 'manager'
                
                ProjectMembership.objects.create(
                    project=project,
                    user=user,
                    role=role
                )
                print(f"Added {user.username} to {project.name} as {role}")
    
    # Create task lists (Kanban columns) for each project
    for project in projects:
        task_lists = []
        
        # Create standard Kanban columns
        for position, (name, description) in enumerate([
            ('Backlog', 'Tasks waiting to be started'),
            ('In Progress', 'Tasks currently being worked on'),
            ('Review', 'Tasks awaiting review or testing'),
            ('Done', 'Completed tasks')
        ]):
            if not TaskList.objects.filter(project=project, name=name).exists():
                task_list = TaskList.objects.create(
                    name=name,
                    description=description,
                    project=project,
                    position=position
                )
                task_lists.append(task_list)
                print(f"Created task list: {name} for {project.name}")
        
        # Create sample tasks
        if project.name == 'E-commerce Website Redesign':
            sample_tasks = [
                ('User Research & Analysis', 'Conduct user interviews and analyze current website usage', 'high', 'Backlog'),
                ('Wireframe Design', 'Create wireframes for key pages', 'high', 'In Progress'),
                ('Homepage Redesign', 'Design new homepage layout and components', 'medium', 'In Progress'),
                ('Product Page Layout', 'Design product detail page with better UX', 'medium', 'Backlog'),
                ('Shopping Cart Flow', 'Redesign checkout process', 'high', 'Review'),
                ('Payment Integration', 'Integrate new payment gateway', 'high', 'Backlog'),
                ('Mobile Responsiveness', 'Ensure all pages work on mobile devices', 'medium', 'Backlog'),
                ('Performance Optimization', 'Optimize images and loading times', 'low', 'Done'),
            ]
        elif project.name == 'Mobile App Development':
            sample_tasks = [
                ('App Architecture Planning', 'Define technical architecture and tech stack', 'high', 'Done'),
                ('User Authentication', 'Implement login/registration functionality', 'high', 'In Progress'),
                ('Profile Management', 'User profile creation and editing', 'medium', 'Backlog'),
                ('Push Notifications', 'Implement push notification system', 'medium', 'Backlog'),
                ('Offline Mode', 'Enable app functionality without internet', 'low', 'Backlog'),
                ('App Store Preparation', 'Prepare app for store submission', 'medium', 'Backlog'),
            ]
        else:  # Data Analytics Dashboard
            sample_tasks = [
                ('Requirements Gathering', 'Collect dashboard requirements from stakeholders', 'high', 'In Progress'),
                ('Data Source Integration', 'Connect to various data sources', 'high', 'Backlog'),
                ('Chart Library Selection', 'Choose appropriate visualization library', 'medium', 'Backlog'),
                ('Dashboard Mockups', 'Create visual mockups of the dashboard', 'medium', 'Backlog'),
                ('Real-time Data Updates', 'Implement real-time data refresh', 'low', 'Backlog'),
            ]
        
        # Create tasks
        for task_name, task_desc, priority, list_name in sample_tasks:
            task_list = TaskList.objects.filter(project=project, name=list_name).first()
            if task_list and not Task.objects.filter(title=task_name, task_list=task_list).exists():
                due_date = datetime.now() + timedelta(days=7 if priority == 'high' else 14)
                
                task = Task.objects.create(
                    title=task_name,
                    description=task_desc,
                    project=project,
                    task_list=task_list,
                    priority=priority,
                    due_date=due_date,
                    created_by=admin,
                    status='completed' if list_name == 'Done' else 'todo'
                )
                
                # Assign task to a team member
                assignee = users[hash(task_name) % len(users)]
                task.assigned_to.add(assignee)
                
                print(f"Created task: {task_name} assigned to {assignee.username}")
    
    print("\nSample data creation completed!")
    print("\nDemo credentials:")
    print("- Admin: admin / admin123")
    print("- John Doe: john_doe / demo123")
    print("- Jane Smith: jane_smith / demo123")
    print("- Mike Wilson: mike_wilson / demo123")

if __name__ == '__main__':
    create_sample_data()
