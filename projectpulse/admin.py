from django.contrib import admin
from .models import *

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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskNoteInline]
    list_display = ('name', 'project', 'assignee', 'start_date', 'due_date', 'status')
    search_fields = ('name', 'project__name', 'assignee__username')
    list_filter = ('status', 'start_date', 'due_date')

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    inlines = [IssueNoteInline]
    list_display = ('title', 'project', 'task', 'reporter', 'assignee', 'status', 'severity', 'created_at')
    search_fields = ('title', 'project__name', 'task__name', 'reporter__username', 'assignee__username')
    list_filter = ('status', 'severity', 'created_at', 'updated_at')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'object_id', 'action_type', 'changed_by', 'timestamp', 'changes')
    search_fields = ('model_name', 'object_id', 'action_type', 'changed_by__username')
    list_filter = ('action_type', 'timestamp')
    readonly_fields = ('model_name', 'object_id', 'action_type', 'changed_by', 'timestamp', 'changes')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")