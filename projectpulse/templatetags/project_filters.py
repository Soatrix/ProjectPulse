# projectpulse/templatetags/project_filters.py
from django import template

register = template.Library()

@register.filter
def count_completed(items):
    try:
        return sum(1 for item in items if item.status == "completed")
    except AttributeError:
        return sum(1 for item in items if item.status == "resolved")
