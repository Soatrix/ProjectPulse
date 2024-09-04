from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os, markdown2, bleach, html
import datetime
from django.core.serializers.json import DjangoJSONEncoder

class ActivityLog(models.Model):
    class ActionType(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        DELETED = 'deleted', 'Deleted'

    model_name = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    action_type = models.CharField(max_length=10, choices=ActionType.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    changes = models.JSONField(default=dict, blank=True, null=True)  # Store changes as a JSON field

    def get_status_color(self):
        if self.model_name == "Task":
            if self.changes and len(self.changes) == 1 and "status" in self.changes:
                if self.changes["status"]["new"] == "not_started" or self.changes["status"]["new"] == "blocked" or self.changes["status"]["new"] == "cancelled":
                    return "danger"
                elif self.changes["status"]["new"] == "in_progress":
                    return "warning"
                else:
                    return "success"
            else:
                return "secondary"
        elif self.model_name == "Project":
            if self.changes and len(self.changes) == 1 and "status" in self.changes:
                if self.changes["status"]["new"] == "not_started" or self.changes["status"]["new"] == "cancelled":
                    return "danger"
                elif self.changes["status"]["new"] == "in_progress" or self.changes["status"]["new"] == "on_hold":
                    return "warning"
                else:
                    return "success"
            else:
                return "secondary"
        elif self.model_name == "Issue":
            if self.changes and len(self.changes) == 1 and "status" in self.changes:
                if self.changes["status"]["new"] == "closed":
                    return "danger"
                elif self.changes["status"]["new"] == "in_progress":
                    return "warning"
                else:
                    return "success"
            else:
                return "secondary"
        else:
            return "secondary"

    def __str__(self):
        return f'{self.get_action_type_display()} {self.model_name} (ID: {self.object_id}) by {self.changed_by} at {self.timestamp}'

    class Meta:
        ordering = ['-timestamp']

class TrackableModel(models.Model):
    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = self.__class__.objects.get(pk=self.pk)
            changes = {}
            for field in self._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(self, field_name)
                if old_value != new_value:
                    # Handle date serialization
                    if isinstance(old_value, (datetime.date, datetime.datetime)):
                        old_value = old_value.isoformat()
                    if isinstance(new_value, (datetime.date, datetime.datetime)):
                        new_value = new_value.isoformat()
                    changes[field_name] = {'old': old_value, 'new': new_value}
            if changes:
                ActivityLog.objects.create(
                    model_name=self.__class__.__name__,
                    object_id=self.pk,
                    action_type=ActivityLog.ActionType.UPDATED,
                    changed_by=self.owner if hasattr(self, 'owner') else None,
                    changes=changes
                )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

def project_image_upload_path(instance, filename):
    # This will upload the image to 'projects/<project_id>/<filename>'
    return os.path.join('static', 'projects', str(instance.id), "profile.png")

class Project(TrackableModel):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        ON_HOLD = 'on_hold', 'On Hold'
        CANCELLED = 'cancelled', 'Cancelled'

    organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
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

    def get_activity_logs(self):
        """
        Retrieve all activity logs related to this project, including logs for
        associated tasks and issues.
        """
        # Fetch logs for the project itself
        project_logs = ActivityLog.objects.filter(
            model_name="Project", object_id=self.id
        )

        # Fetch logs for associated tasks
        task_logs = ActivityLog.objects.filter(
            Q(model_name="Task") & Q(object_id__in=self.tasks.values_list('id', flat=True))
        )

        # Fetch logs for associated issues
        issue_logs = ActivityLog.objects.filter(
            Q(model_name="Issue") & Q(object_id__in=self.issues.values_list('id', flat=True))
        )

        # Combine all logs and order them by timestamp
        all_logs = project_logs | task_logs | issue_logs
        return all_logs.order_by('-timestamp')

    def description_markdown(self):
        text = markdown2.markdown(self.description, extras=["cuddled-lists"])
        html_cleaned = bleach.clean(text)
        html_linked = bleach.linkify(html_cleaned)
        return html.unescape(html_linked)

    def total_tasks(self):
        return self.tasks.count()

    def total_tasks_completed(self):
        return sum(1 for task in self.tasks.all() if task.status == "completed")

    def total_issues(self):
        return self.issues.count()

    def total_issues_resolved(self):
        return sum(1 for issue in self.issues.all() if issue.status == "resolved")

    def total_tasks_overdue(self):
        """Return the total number of overdue tasks for the project."""
        return self.tasks.filter(due_date__lt=timezone.now().date(), status__in=[Task.Status.NOT_STARTED, Task.Status.IN_PROGRESS])

    def total_tasks_due_today(self):
        """Return the total number of tasks due today."""
        return self.tasks.filter(due_date=timezone.now().date())

    def total_tasks_due_this_week(self):
        """Return the total number of tasks due this week."""
        today = timezone.now().date()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)
        return self.tasks.filter(due_date__range=[start_of_week, end_of_week])
    def total_issues_open(self):
        """Return the total number of open issues for the project."""
        return self.issues.filter(status=Issue.Status.OPEN)

    def total_issues_severity(self, severity):
        """Return the total number of issues with a given severity."""
        return self.issues.filter(severity=severity)

class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Note by {self.author} on {self.project.name}'

class Task(TrackableModel):
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

    def is_overdue(self):
        """Check if the task is overdue."""
        return self.due_date and self.due_date < timezone.now().date() and self.status not in [Task.Status.COMPLETED, Task.Status.CANCELLED]

    def days_remaining(self):
        """Return the number of days remaining until the task's due date."""
        if self.due_date:
            return (self.due_date - timezone.now().date()).days
        return None

    def is_due_today(self):
        """Check if the task is due today."""
        return self.due_date == timezone.now().date()

    def total_requirements_completed(self):
        """Return the total number of completed requirements for this task."""
        return sum(1 for task in self.requirements.all() if task.status == Task.Status.COMPLETED) + \
               sum(1 for issue in self.issues.all() if issue.status == Issue.Status.RESOLVED)

class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='task_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Note by {self.author} on {self.task.name}'

class Issue(TrackableModel):
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

    def is_overdue(self):
        """Check if the issue is overdue."""
        return self.updated_at < timezone.now() and self.status not in [Issue.Status.RESOLVED, Issue.Status.CLOSED]

    def days_open(self):
        """Return the number of days the issue has been open."""
        return (timezone.now().date() - self.created_at.date()).days

    def is_open(self):
        """Check if the issue is open."""
        return self.status == Issue.Status.OPEN

    def total_notes(self):
        """Return the total number of notes on the issue."""
        return self.notes.count()

class IssueNote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issue_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Note by {self.author} on {self.issue.title}'

def organization_image_upload_path(instance, filename):
    # This will upload the image to 'organizations/<project_id>/<filename>'
    return os.path.join('static', 'organizations', str(instance.id), filename)

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    members = models.ManyToManyField(User, related_name='organizations', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logo = models.ImageField(upload_to=organization_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Project)
@receiver(post_save, sender=Task)
@receiver(post_save, sender=Issue)
def log_model_change(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            model_name=sender.__name__,
            object_id=instance.id,
            action_type=ActivityLog.ActionType.CREATED,
            changed_by=instance.owner if hasattr(instance, 'owner') else None
        )
    # `changes` field will be populated in the overridden `save` method

@receiver(post_delete, sender=Project)
@receiver(post_delete, sender=Task)
@receiver(post_delete, sender=Issue)
def log_model_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        model_name=sender.__name__,
        object_id=instance.id,
        action_type=ActivityLog.ActionType.DELETED,
        changed_by=instance.owner if hasattr(instance, 'owner') else None
    )