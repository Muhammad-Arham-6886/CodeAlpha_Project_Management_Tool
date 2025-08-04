from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
import uuid


class Project(models.Model):
    """Main project model for organizing tasks and teams"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_projects'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        related_name='projects'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    progress = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Manual progress percentage (0-100)"
    )
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['owner', 'created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def completion_percentage(self):
        """Calculate project completion based on tasks"""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)

    @property
    def total_members(self):
        """Get total number of project members"""
        return self.members.count()

    def is_member(self, user):
        """Check if a user is a member of this project"""
        return self.members.filter(id=user.id).exists()

    def can_edit(self, user):
        """Check if user can edit this project"""
        return (
            user == self.owner or
            self.projectmembership_set.filter(
                user=user, 
                role__in=['admin', 'manager']
            ).exists()
        )


class ProjectMembership(models.Model):
    """Through model for project membership with roles"""
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('project', 'user')
        indexes = [
            models.Index(fields=['project', 'role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class ProjectInvitation(models.Model):
    """Model for inviting users to projects"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_invitations'
    )
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_invitations',
        null=True, 
        blank=True
    )
    email = models.EmailField(help_text="Email of the person to invite")
    role = models.CharField(max_length=20, choices=ProjectMembership.ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Optional invitation message")
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('project', 'email')
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['status', 'expires_at']),
        ]

    def __str__(self):
        return f"Invitation to {self.project.name} for {self.email}"

    def is_expired(self):
        """Check if invitation has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
