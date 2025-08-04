from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectMembership
from task_management.models import Task
from notification_system.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing the project management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Check existing data
        users_count = User.objects.all().count()
        projects_count = Project.objects.all().count()
        tasks_count = Task.objects.all().count()
        notifications_count = Notification.objects.all().count()
        
        self.stdout.write(f'Current data:')
        self.stdout.write(f'Users: {users_count}')
        self.stdout.write(f'Projects: {projects_count}')
        self.stdout.write(f'Tasks: {tasks_count}')
        self.stdout.write(f'Notifications: {notifications_count}')
        
        if projects_count > 0:
            self.stdout.write(self.style.WARNING('Sample data already exists. Skipping creation.'))
            return
        
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')
        
        # Create test users
        test_user1, created = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created:
            test_user1.set_password('password123')
            test_user1.save()
            self.stdout.write(f'Created test user: {test_user1.username}')
        
        test_user2, created = User.objects.get_or_create(
            username='jane_smith',
            defaults={
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        )
        if created:
            test_user2.set_password('password123')
            test_user2.save()
            self.stdout.write(f'Created test user: {test_user2.username}')
        
        # Create sample projects
        project1 = Project.objects.create(
            name='Website Redesign',
            description='Complete redesign of company website with modern UI/UX and improved user experience. This project includes wireframing, design, development, and testing phases.',
            status='active',
            priority='high',
            owner=admin_user,
            color='#667eea'
        )
        self.stdout.write(f'Created project: {project1.name}')
        
        project2 = Project.objects.create(
            name='Mobile App Development',
            description='Develop cross-platform mobile application for iOS and Android with React Native. Includes user authentication, data synchronization, and push notifications.',
            status='planning',
            priority='medium',
            owner=admin_user,
            color='#48bb78'
        )
        self.stdout.write(f'Created project: {project2.name}')
        
        project3 = Project.objects.create(
            name='Marketing Campaign Q4',
            description='Comprehensive Q4 marketing campaign for product launch including social media, email marketing, and content creation.',
            status='active',
            priority='high',
            owner=test_user1,
            color='#ed8936'
        )
        self.stdout.write(f'Created project: {project3.name}')
        
        project4 = Project.objects.create(
            name='Database Migration',
            description='Migrate legacy database to new cloud infrastructure with improved performance and security.',
            status='on_hold',
            priority='low',
            owner=admin_user,
            color='#f56565'
        )
        self.stdout.write(f'Created project: {project4.name}')
        
        # Add project memberships
        ProjectMembership.objects.create(project=project1, user=admin_user, role='admin')
        ProjectMembership.objects.create(project=project1, user=test_user1, role='member')
        ProjectMembership.objects.create(project=project1, user=test_user2, role='member')
        
        ProjectMembership.objects.create(project=project2, user=admin_user, role='admin')
        ProjectMembership.objects.create(project=project2, user=test_user2, role='manager')
        
        ProjectMembership.objects.create(project=project3, user=test_user1, role='admin')
        ProjectMembership.objects.create(project=project3, user=admin_user, role='member')
        
        ProjectMembership.objects.create(project=project4, user=admin_user, role='admin')
        
        self.stdout.write('Created project memberships')
        
        # Create sample tasks
        task1 = Task.objects.create(
            project=project1,
            title='Design Homepage Layout',
            description='Create wireframes and mockups for the new homepage design. Include responsive layouts for desktop, tablet, and mobile devices.',
            status='todo',
            priority='high',
            created_by=admin_user
        )
        task1.assigned_to.add(test_user2)
        
        task2 = Task.objects.create(
            project=project1,
            title='Implement Navigation Menu',
            description='Code the responsive navigation menu component with dropdown functionality and mobile hamburger menu.',
            status='in_progress',
            priority='medium',
            created_by=admin_user
        )
        task2.assigned_to.add(test_user1)
        
        task3 = Task.objects.create(
            project=project1,
            title='Setup Database Schema',
            description='Design and implement the database structure for user management, content management, and analytics.',
            status='completed',
            priority='high',
            created_by=admin_user
        )
        task3.assigned_to.add(admin_user)
        
        task4 = Task.objects.create(
            project=project1,
            title='Content Management System',
            description='Develop CMS functionality for easy content updates and blog management.',
            status='review',
            priority='medium',
            created_by=test_user1
        )
        task4.assigned_to.add(test_user2)
        
        task5 = Task.objects.create(
            project=project2,
            title='Market Research',
            description='Conduct comprehensive market research for mobile app features and competitor analysis.',
            status='todo',
            priority='medium',
            created_by=admin_user
        )
        task5.assigned_to.add(test_user2)
        
        task6 = Task.objects.create(
            project=project2,
            title='App Architecture Planning',
            description='Define the technical architecture, technology stack, and development roadmap.',
            status='in_progress',
            priority='high',
            created_by=admin_user
        )
        task6.assigned_to.add(admin_user)
        
        task7 = Task.objects.create(
            project=project3,
            title='Content Creation',
            description='Create engaging marketing content for social media campaigns including graphics, videos, and copy.',
            status='todo',
            priority='medium',
            created_by=test_user1
        )
        task7.assigned_to.add(test_user1)
        
        task8 = Task.objects.create(
            project=project3,
            title='Email Campaign Setup',
            description='Design and setup automated email marketing campaigns for lead nurturing.',
            status='completed',
            priority='high',
            created_by=test_user1
        )
        task8.assigned_to.add(admin_user)
        
        self.stdout.write('Created 8 sample tasks')
        
        # Create sample notifications
        Notification.objects.create(
            recipient=test_user1,
            sender=admin_user,
            title='Welcome to Website Redesign Project',
            message='You have been added to the Website Redesign project as a team member. Check out the project details and upcoming tasks.',
            notification_type='project_invitation',
            project=project1
        )
        
        Notification.objects.create(
            recipient=test_user2,
            sender=admin_user,
            title='New Task Assigned: Design Homepage Layout',
            message='You have been assigned to work on the homepage design task. Please review the requirements and start working on the wireframes.',
            notification_type='task_assigned',
            project=project1,
            task=task1
        )
        
        Notification.objects.create(
            recipient=admin_user,
            sender=test_user1,
            title='Task Status Update',
            message='The Implement Navigation Menu task has been moved to in progress status.',
            notification_type='task_updated',
            project=project1,
            task=task2
        )
        
        Notification.objects.create(
            recipient=test_user2,
            sender=admin_user,
            title='Project Role Updated',
            message='You have been promoted to Manager role in the Mobile App Development project.',
            notification_type='member_added',
            project=project2
        )
        
        Notification.objects.create(
            recipient=test_user1,
            sender=admin_user,
            title='Task Completed',
            message='Great job! The Database Schema Setup task has been marked as completed.',
            notification_type='task_completed',
            project=project1,
            task=task3
        )
        
        self.stdout.write('Created 5 sample notifications')
        
        # Final summary
        final_users = User.objects.all().count()
        final_projects = Project.objects.all().count()
        final_tasks = Task.objects.all().count()
        final_notifications = Notification.objects.all().count()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total Users: {final_users}'))
        self.stdout.write(self.style.SUCCESS(f'Total Projects: {final_projects}'))
        self.stdout.write(self.style.SUCCESS(f'Total Tasks: {final_tasks}'))
        self.stdout.write(self.style.SUCCESS(f'Total Notifications: {final_notifications}'))
        
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('Admin: username=admin, password=admin123')
        self.stdout.write('User 1: username=john_doe, password=password123')
        self.stdout.write('User 2: username=jane_smith, password=password123')
