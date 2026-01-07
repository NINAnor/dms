from urllib.parse import urlparse

import mistune
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def markdown(value):
    return mark_safe(mistune.html(value))  # noqa: S308


@register.filter
def parse_uri_part(value: str, part: str) -> str | None:
    try:
        return getattr(urlparse(value), part)
    except ValueError:
        return None
