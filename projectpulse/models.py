from django.db import models
from django.contrib.auth.models import User
import os

def project_image_upload_path(instance, filename):
    # This will upload the image to 'projects/<project_id>/<filename>'
    return os.path.join('static', 'projects', str(instance.id), "profile.png")

class Project(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        ON_HOLD = 'on_hold', 'On Hold'
        CANCELLED = 'cancelled', 'Cancelled'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.NOT_STARTED)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, null=True)

    # Logo/Profile Image
    logo = models.ImageField(upload_to=project_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Note by {self.author} on {self.project.name}'

class Task(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        BLOCKED = 'blocked', 'Blocked'
        CANCELLED = 'cancelled', 'Cancelled'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    start_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.NOT_STARTED)

    # Task dependencies
    requirements = models.ManyToManyField('self', blank=True, related_name='waited_on', symmetrical=False)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name

    def total_requirements(self):
        return self.requirements.count() + self.issues.count()

    def completed_requirements(self):
        return sum(1 for task in self.requirements.all() if task.status in [Task.Status.COMPLETED, Task.Status.CANCELLED, Task.Status.BLOCKED]) + sum(1 for issue in self.issues.all() if issue.status in [Issue.Status.RESOLVED, Issue.Status.CLOSED])

class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='task_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Note by {self.author} on {self.task.name}'

class Issue(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues', blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='issues', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.OPEN)
    severity = models.CharField(max_length=50, choices=Severity.choices, default=Severity.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.title

class IssueNote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issue_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Note by {self.author} on {self.issue.title}'
