from django.urls import path
from . import views, api

app_name = 'tasks'

urlpatterns = [
    # Task management views
    path('', views.task_list, name='task_list'),
    path('create/', views.create_task, name='create_task'),
    path('<uuid:task_id>/', views.task_detail, name='task_detail'),
    path('<uuid:task_id>/edit/', views.edit_task, name='edit_task'),
    path('<uuid:task_id>/delete/', views.delete_task, name='delete_task'),
    path('<uuid:task_id>/complete/', views.toggle_task_completion, name='toggle_task_completion'),
    path('<uuid:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('project/<uuid:project_id>/', views.project_tasks, name='project_tasks'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    
    # API endpoints
    path('api/project/<uuid:project_id>/members/', api.get_project_members, name='api_project_members'),
]
