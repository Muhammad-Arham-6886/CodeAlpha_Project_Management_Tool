from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment, TaskActivity


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'project']
    search_fields = ['title', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'completed_date']
    filter_horizontal = ['assigned_to']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'project', 'created_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Dates & Time', {
            'fields': ('start_date', 'due_date', 'estimated_hours', 'actual_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'author__username', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'task', 'uploaded_by', 'uploaded_at', 'file_size_human']
    list_filter = ['uploaded_at']
    search_fields = ['original_name', 'task__title', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['created_at']
