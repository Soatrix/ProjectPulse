from django.db import models
from django.contrib.auth.models import User
import os

def project_image_upload_path(instance, filename):
    # This will upload the image to 'projects/<project_id>/<filename>'
    return os.path.join('projects', str(instance.id), "profile.png")

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ], default='not_started')

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, null=True)

    # Logo/Profile Image
    logo = models.ImageField(upload_to=project_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    start_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled'),
    ], default='not_started')

    # Task dependencies
    requirements = models.ManyToManyField('self', blank=True, related_name='requirements', symmetrical=False)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name


class Issue(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues', blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='issues', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    status = models.CharField(max_length=50, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], default='open')
    severity = models.CharField(max_length=50, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.title