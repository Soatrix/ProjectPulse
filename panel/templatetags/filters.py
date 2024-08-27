from django import template

register = template.Library()


@register.filter
def split_string(value, delimiter_and_index):
    """
    Splits the string by a specified delimiter and returns the element at the given index.

    Usage: {{ value|split_string:"delimiter:index" }}
    Example: {{ "apple,orange,banana"|split_string:",:1" }} will return "orange"
    """
    try:
        delimiter, index = delimiter_and_index.split(':')
        index = int(index)  # Convert the index to an integer
        parts = str(value).split(delimiter)  # Split the string by the specified delimiter
        return parts[index]
    except (ValueError, IndexError):
        return ''  # Return an empty string if there's an error or index is out of range

@register.filter
def has_permission(user, permission):
    """
    Check if the user has the specified permission.
    """
    return user.has_perm(f"{permission.content_type.app_label}.{permission.codename}")