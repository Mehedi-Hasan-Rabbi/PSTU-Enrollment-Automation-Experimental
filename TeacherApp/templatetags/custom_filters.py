from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    if d is None:
        return None  # Handle NoneType dictionary
    return d.get(key, None)
