from django.contrib import admin
from .models import Project, Task, Issue


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


class IssueInline(admin.TabularInline):
    model = Issue
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'start_date', 'end_date', 'status')
    search_fields = ('name', 'owner__username', 'description')
    list_filter = ('status', 'start_date', 'end_date')
    inlines = [TaskInline, IssueInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner', 'members', 'start_date', 'end_date', 'status')
        }),
        ('Custom Fields', {
            'fields': ('custom_fields',)
        }),
        ('Logo', {
            'fields': ('logo',),
        }),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'assignee', 'start_date', 'due_date', 'status')
    search_fields = ('name', 'project__name', 'assignee__username', 'description')
    list_filter = ('status', 'start_date', 'due_date', 'project')
    inlines = [IssueInline]

    fieldsets = (
        (None, {
            'fields': ('project', 'name', 'description', 'assignee', 'start_date', 'due_date', 'status')
        }),
        ('Requirements', {
            'fields': ('requirements',)
        }),
        ('Custom Fields', {
            'fields': ('custom_fields',)
        }),
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
    'title', 'project', 'task', 'reporter', 'assignee', 'status', 'severity', 'created_at', 'updated_at')
    search_fields = ('title', 'project__name', 'task__name', 'reporter__username', 'assignee__username', 'description')
    list_filter = ('status', 'severity', 'created_at', 'updated_at', 'project', 'task')

    fieldsets = (
        (None, {
            'fields': ('project', 'task', 'title', 'description', 'reporter', 'assignee', 'status', 'severity')
        }),
        ('Custom Fields', {
            'fields': ('custom_fields',)
        }),
    )