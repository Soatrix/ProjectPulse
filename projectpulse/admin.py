from django.contrib import admin
from .models import Project, ProjectNote, Task, TaskNote, Issue, IssueNote, ActivityLog

class ProjectNoteInline(admin.TabularInline):
    model = ProjectNote
    extra = 1

class TaskNoteInline(admin.TabularInline):
    model = TaskNote
    extra = 1

class IssueNoteInline(admin.TabularInline):
    model = IssueNote
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectNoteInline]
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
    inlines = [TaskNoteInline]
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
    inlines = [IssueNoteInline]
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

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'object_id', 'action_type', 'changed_by', 'timestamp', 'changes')
    search_fields = ('model_name', 'object_id', 'action_type', 'changed_by__username')
    list_filter = ('action_type', 'timestamp')
    readonly_fields = ('model_name', 'object_id', 'action_type', 'changed_by', 'timestamp', 'changes')
