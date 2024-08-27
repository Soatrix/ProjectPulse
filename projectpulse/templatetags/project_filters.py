# projectpulse/templatetags/project_filters.py
from django import template

register = template.Library()

@register.filter
def count_completed(items):
    return sum(1 for item in items if item.status == "completed")

@register.filter
def count_resolved(items):
    return sum(1 for item in items if item.status == "resolved")