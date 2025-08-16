from django import template

register = template.Library()

@register.filter
def get(mapping, key):
    """
    Template filter to access dict[key] safely.
    Usage: {{ mydict|get:some_key }}
    """
    try:
        return mapping.get(key, "")
    except Exception:
        return ""