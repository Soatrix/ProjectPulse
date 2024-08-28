# projectpulse/templatetags/project_filters.py
from django import template

register = template.Library()

@register.filter
def count_completed(tasks):
    return sum(1 for task in tasks if task.status == "completed" or task.status == "cancelled" or task.status == "blocked")

@register.filter
def count_resolved(issues):
    return sum(1 for issue in issues if issue.status == "resolved" or issue.status == "closed")

@register.filter
def sum_count_completed(tasks, issues):
    return sum(1 for task in tasks if task.status == "completed" or task.status == "cancelled" or task.status == "blocked") + sum(1 for issue in issues if issue.status == "resolved" or issue.status == "closed")