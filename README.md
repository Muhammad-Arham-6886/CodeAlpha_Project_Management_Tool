# Project Management Tool

A comprehensive Django-based project management application similar to Trello/Asana, featuring real-time collaboration, task management, and team coordination.

## 🚀 Features

### Core Functionality
- **User Authentication & Profiles**: Custom user system with extended profiles
- **Project Management**: Create and manage multiple projects with team collaboration
- **Task Management**: Kanban-style boards with drag-and-drop functionality
- **Real-time Communication**: Comments, notifications, and live updates
- **Team Collaboration**: Invite members, assign roles, and manage permissions
- **File Attachments**: Upload and share files within tasks
- **Activity Tracking**: Complete audit trail of all project activities

### Advanced Features
- **Real-time Updates**: WebSocket integration for live collaboration
- **Notification System**: In-app and email notifications with user preferences
- **Task Organization**: Lists/columns, tags, priorities, and due dates
- **Progress Tracking**: Visual progress indicators and completion statistics
- **Search & Filtering**: Advanced search and filtering capabilities
- **Responsive Design**: Mobile-friendly interface with modern UI

## 🛠 Technology Stack

### Backend
- **Django 5.2.4**: Python web framework
- **Django REST Framework**: API development
- **Django Channels**: WebSocket support for real-time features
- **SQLite**: Database (development) / PostgreSQL (production ready)
- **Redis**: Channel layer for WebSocket scaling

### Frontend
- **HTML5/CSS3**: Modern markup and styling
- **JavaScript**: Interactive functionality
- **Bootstrap 5**: Responsive UI framework
- **WebSocket API**: Real-time communication

### Additional Libraries
- **Pillow**: Image processing for avatars and attachments
- **django-cors-headers**: CORS handling for API access

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- pip package manager
- Redis server (for WebSocket functionality)

### 1. Clone and Setup
```bash
cd CodeAlpha_ProjectManagementTool
```

### 2. Virtual Environment
```bash
# Create virtual environment
python -m venv project_env

# Activate virtual environment
# Windows:
project_env\Scripts\activate
# Linux/Mac:
source project_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install django djangorestframework django-channels channels-redis django-cors-headers pillow
```

### 4. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (already created: admin/admin123)
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## 🏗 Project Structure

```
CodeAlpha_ProjectManagementTool/
├── project_manager/          # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── asgi.py              # ASGI configuration for WebSockets
│   └── wsgi.py              # WSGI configuration
├── accounts/                # User management app
│   ├── models.py            # User and UserProfile models
│   ├── views.py             # Authentication views
│   └── urls.py              # Account-related URLs
├── projects/                # Project management app
│   ├── models.py            # Project, ProjectMembership models
│   ├── views.py             # Project views
│   ├── urls.py              # Project URLs
│   └── api_views.py         # API endpoints
├── tasks/                   # Task management app
│   ├── models.py            # Task, TaskList, TaskComment models
│   ├── views.py             # Task views
│   └── api_views.py         # Task API endpoints
├── notifications/           # Notification system
│   ├── models.py            # Notification models
│   ├── consumers.py         # WebSocket consumers
│   ├── routing.py           # WebSocket routing
│   └── api_views.py         # Notification API
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploads
├── templates/               # HTML templates (to be created)
└── manage.py                # Django management script
```

## 📊 Database Models

### User Management
- **User**: Extended Django user with avatar, bio, company info
- **UserProfile**: Additional profile data and preferences

### Project Management
- **Project**: Main project entity with status, priority, dates
- **ProjectMembership**: User roles within projects (member/manager/admin)
- **ProjectInvitation**: System for inviting users to projects

### Task Management
- **TaskList**: Kanban columns/lists for organizing tasks
- **Task**: Individual tasks with assignments, due dates, progress
- **TaskComment**: Communication within tasks
- **TaskTag**: Categorization system for tasks
- **TaskAttachment**: File uploads for tasks
- **TaskActivity**: Audit trail of all task changes

### Notifications
- **Notification**: Real-time notifications for users
- **NotificationPreference**: User notification settings

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Redis Setup (for WebSockets)
Install and start Redis server:
```bash
# Windows: Download Redis for Windows
# Linux: sudo apt install redis-server
# Mac: brew install redis

# Start Redis
redis-server
```

## 🚦 API Endpoints

### Projects API
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Tasks API
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Notifications API
- `GET /api/notifications/` - List user notifications
- `POST /api/notifications/mark-all-read/` - Mark all as read

## 🔌 WebSocket Events

### Real-time Features
- **Project Updates**: Live project changes
- **Task Updates**: Real-time task modifications
- **Comments**: Instant comment notifications
- **User Activity**: Live user presence indicators

### WebSocket Endpoints
- `ws/notifications/{user_id}/` - User notifications
- `ws/project/{project_id}/` - Project-specific updates
- `ws/task/{task_id}/` - Task-specific updates

## 👥 User Roles & Permissions

### Project Roles
- **Owner**: Full project control (creator)
- **Admin**: Manage members and settings
- **Manager**: Assign tasks and manage workflow
- **Member**: Create and work on tasks

### Permissions
- Project owners can delete projects
- Admins/Managers can invite members
- All members can create and comment on tasks
- Users can only edit their own profiles

## 🎨 Frontend Development

### Template System
- Base template with navigation and notifications
- Responsive design with Bootstrap 5
- AJAX integration for dynamic updates
- WebSocket integration for real-time features

### Key UI Components
- **Dashboard**: Project overview and quick access
- **Kanban Board**: Drag-and-drop task management
- **Task Detail**: Comprehensive task view with comments
- **Project Settings**: Team and configuration management

## 🧪 Testing

Run the development server and test:
```bash
python manage.py runserver
```

### Test Accounts
- **Admin**: username: `admin`, password: `admin123`
- Create additional users through the registration system

### Test Workflow
1. Login as admin
2. Create a new project
3. Invite team members
4. Create task lists (columns)
5. Add tasks and assignments
6. Test real-time updates with multiple users

## 📝 Development Status

### ✅ Completed
- [x] Project structure and configuration
- [x] Database models and relationships
- [x] User authentication system
- [x] Basic URL routing
- [x] Database migrations
- [x] Admin interface setup
- [x] WebSocket configuration

### 🚧 In Progress
- [ ] Frontend templates and views
- [ ] API implementation
- [ ] WebSocket consumers
- [ ] Real-time features
- [ ] File upload handling

### 📋 Todo
- [ ] Complete UI/UX implementation
- [ ] Email notification system
- [ ] Advanced search and filtering
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Deployment configuration

## 🚀 Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set up Redis cluster
- [ ] Configure email service
- [ ] Set up static file serving
- [ ] Configure HTTPS
- [ ] Set up monitoring and logging

### Recommended Hosting
- **Backend**: Heroku, DigitalOcean, AWS
- **Database**: PostgreSQL (Heroku Postgres, AWS RDS)
- **Redis**: Redis Cloud, AWS ElastiCache
- **Static Files**: AWS S3, Cloudinary

## 📚 Documentation

For detailed documentation on specific features:
- See individual app README files
- Check docstrings in model and view files
- Refer to Django and DRF documentation
- WebSocket implementation using Django Channels

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is part of the CodeAlpha internship program and is for educational purposes.

## 🆘 Support

For issues and questions:
- Check the Django documentation
- Review the project's GitHub issues
- Contact the development team

---

**Built with ❤️ for CodeAlpha - Project Management Excellence**
