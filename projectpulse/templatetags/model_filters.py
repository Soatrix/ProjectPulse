from django import template
from django.apps import apps

register = template.Library()

@register.filter
def get_object(model_name, object_id):
    """
    Retrieve an object from the model based on its ID.

    Usage in template: {{ model_name|get_object:object_id }}
    """
    try:
        model = apps.get_model(app_label='projectpulse', model_name=model_name)
        return model.objects.get(id=object_id)
    except (model.DoesNotExist, ValueError, TypeError) as e:
        return None


@register.filter
def dict_keys(value):
    """
    Returns the keys of the dictionary as a list.

    Usage in a template:
    {{ my_dict|dict_keys }}
    """
    if isinstance(value, dict):
        return list(value.keys())
    return []

@register.filter
def format_list(value):
    """
    Format a list as a comma-separated string with the final item preceded by '&'.

    Usage in template: {{ my_list|format_list }}
    """
    if not isinstance(value, list):
        return value

    if len(value) == 0:
        return ''

    if len(value) == 1:
        return str(value[0])

    return ', '.join(map(str, value[:-1])) + ' & ' + str(value[-1])

@register.filter
def reverse_slugify(string: str):
    return string.replace("-", " ").replace("_", " ").title()