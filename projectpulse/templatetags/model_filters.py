from django import template
from django.apps import apps

register = template.Library()

@register.filter
def get_object(model_name_id_tuple, object_id):
    """
    Retrieve an object from the model based on its ID.

    Usage in template: {{ model_name|get_object:object_id }}
    """
    model_name, model_id = model_name_id_tuple
    try:
        model = apps.get_model(app_label='projectpulse', model_name=model_name)
        return model.objects.get(id=object_id)
    except (model.DoesNotExist, ValueError, TypeError) as e:
        return None
