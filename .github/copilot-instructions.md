<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Project Management Tool - Copilot Instructions

This is a Django-based Project Management Tool similar to Trello/Asana with the following features:

## Tech Stack
- **Backend**: Django 5.2.4 + Django REST Framework
- **Real-time**: Django Channels (WebSockets) + Redis
- **Database**: SQLite (development)
- **Frontend**: HTML/CSS/JavaScript with Bootstrap 5
- **Authentication**: Custom User model extending AbstractUser

## Architecture
- **Apps**: accounts, projects, tasks, notifications
- **Models**: User, Project, Task, TaskList, Notification, etc.
- **API**: RESTful API endpoints for all CRUD operations
- **WebSockets**: Real-time notifications and collaborative features

## Key Features
- User authentication and profiles
- Project creation and team management
- Kanban-style task boards with drag-and-drop
- Task assignment and commenting
- Real-time notifications
- File attachments
- Activity tracking

## Code Style Guidelines
- Follow Django best practices
- Use Django REST Framework serializers for API responses
- Implement proper permissions and authentication
- Use UUID for primary keys where security is important
- Follow PEP 8 for Python code formatting
- Use meaningful variable and function names
- Add docstrings to all classes and functions

## Database Design
- Custom User model with extended profile information
- Project-based organization with team membership
- Task hierarchy with lists/columns (Kanban style)
- Notification system for real-time updates
- Activity logging for audit trails

## API Design
- RESTful endpoints with proper HTTP methods
- Consistent response formats
- Proper error handling and status codes
- Pagination for list endpoints
- Filtering and searching capabilities

## WebSocket Implementation
- Separate consumers for notifications, projects, and tasks
- Channel groups for real-time collaboration
- Authentication and permission checks
- Graceful error handling

When generating code:
1. Ensure all models have proper relationships and constraints
2. Include proper validation and error handling
3. Follow the established patterns for serializers and views
4. Use appropriate permissions for API endpoints
5. Include WebSocket events for real-time features
6. Add proper logging and monitoring
7. Consider performance implications and optimize queries
8. Include comprehensive tests for all functionality
