from django.contrib import admin
from .models import Project, ProjectNote, Task, TaskNote, Issue, IssueNote, ActivityLog
from django.utils.html import format_html
from django.contrib.auth.models import User
import json

class ProjectNoteInline(admin.TabularInline):
    model = ProjectNote
    extra = 1

class TaskNoteInline(admin.TabularInline):
    model = TaskNote
    extra = 1

class IssueNoteInline(admin.TabularInline):
    model = IssueNote
    extra = 1

class ActivityLogInline(admin.TabularInline):
    model = ActivityLog
    extra = 0
    readonly_fields = ('timestamp', 'model_name', 'action_type', 'object_id', 'changed_by', 'changes')
    can_delete = False
    verbose_name = 'Activity Log'
    verbose_name_plural = 'Activity Logs'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If an instance is being edited
            return self.readonly_fields + ('model_name', 'object_id', 'action_type', 'changed_by', 'timestamp', 'changes')
        return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectNoteInline, ActivityLogInline]
    list_display = ('name', 'owner', 'start_date', 'end_date', 'status')
    search_fields = ('name', 'owner__username')
    list_filter = ('status', 'start_date', 'end_date')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:  # If the object is being changed (not created)
            changes = self.get_changes(obj)
            ActivityLog.objects.create(
                model_name=obj.__class__.__name__,
                object_id=obj.pk,
                action_type=ActivityLog.ActionType.UPDATED,
                changed_by=request.user,
                changes=changes
            )

    def get_changes(self, obj):
        changes = {}
        for field in obj._meta.fields:
            field_name = field.name
            old_value = obj.__class__.objects.get(pk=obj.pk).get_field_value(field_name)
            new_value = getattr(obj, field_name)
            if old_value != new_value:
                changes[field_name] = {'old': old_value, 'new': new_value}
        return changes

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskNoteInline, ActivityLogInline]
    list_display = ('name', 'project', 'assignee', 'start_date', 'due_date', 'status')
    search_fields = ('name', 'project__name', 'assignee__username')
    list_filter = ('status', 'start_date', 'due_date')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:  # If the object is being changed (not created)
            changes = self.get_changes(obj)
            ActivityLog.objects.create(
                model_name=obj.__class__.__name__,
                object_id=obj.pk,
                action_type=ActivityLog.ActionType.UPDATED,
                changed_by=request.user,
                changes=changes
            )

    def get_changes(self, obj):
        changes = {}
        for field in obj._meta.fields:
            field_name = field.name
            old_value = obj.__class__.objects.get(pk=obj.pk).get_field_value(field_name)
            new_value = getattr(obj, field_name)
            if old_value != new_value:
                changes[field_name] = {'old': old_value, 'new': new_value}
        return changes

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    inlines = [IssueNoteInline, ActivityLogInline]
    list_display = ('title', 'project', 'task', 'reporter', 'assignee', 'status', 'severity', 'created_at')
    search_fields = ('title', 'project__name', 'task__name', 'reporter__username', 'assignee__username')
    list_filter = ('status', 'severity', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:  # If the object is being changed (not created)
            changes = self.get_changes(obj)
            ActivityLog.objects.create(
                model_name=obj.__class__.__name__,
                object_id=obj.pk,
                action_type=ActivityLog.ActionType.UPDATED,
                changed_by=request.user,
                changes=changes
            )

    def get_changes(self, obj):
        changes = {}
        for field in obj._meta.fields:
            field_name = field.name
            old_value = obj.__class__.objects.get(pk=obj.pk).get_field_value(field_name)
            new_value = getattr(obj, field_name)
            if old_value != new_value:
                changes[field_name] = {'old': old_value, 'new': new_value}
        return changes

    def get_field_value(self, field_name):
        """Helper method to get the field value."""
        return getattr(self, field_name, None)
