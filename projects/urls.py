from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('create/', views.create_project, name='create_project'),
    path('<uuid:project_id>/', views.project_detail, name='project_detail'),
    path('<uuid:project_id>/edit/', views.edit_project, name='edit_project'),
    path('<uuid:project_id>/delete/', views.delete_project, name='delete_project'),
    path('<uuid:project_id>/members/', views.project_members, name='project_members'),
    path('<uuid:project_id>/invite/', views.invite_member, name='invite_member'),
    path('<uuid:project_id>/board/', views.project_board, name='project_board'),
]
