import re
from django import template

register = template.Library()


@register.filter
def split(value, separator):
    """
    Split a string by a separator.
    
    Example: "a,b,c"|split:"," -> ['a', 'b', 'c']
    """
    if not value:
        return []
    return value.split(separator)


@register.filter
def strip(value):
    """
    Remove leading and trailing whitespace from a string.
    
    Example: "  hello  "|strip -> "hello"
    """
    if not value:
        return ""
    return str(value).strip()


@register.filter
def phone_to_tel(phone_string):
    """
    Convert a phone number string to a tel: link format.
    Removes all non-digit characters.
    
    Example: "+1 (416) 710-0361" -> "+14167100361"
    """
    if not phone_string:
        return ""
    # Remove all non-digit characters except leading +
    cleaned = re.sub(r'[^\d+]', '', phone_string)
    # Ensure it starts with + and has digits
    if cleaned and not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    return cleaned


@register.filter
def format_phone_display(phone_string):
    """
    Clean and prepare phone number for display.
    Removes excess whitespace.
    """
    if not phone_string:
        return ""
    return phone_string.strip()
