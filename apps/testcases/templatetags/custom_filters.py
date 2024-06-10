# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2024/6/9 14:57

from django import template
import json
from datetime import datetime


register = template.Library()

@register.filter
def default_if_none(value, default_value=''):
    """Returns the default value if the given value is None."""
    return default_value if value is None else value

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@register.filter
def to_js(value):
    """Converts Python objects to JSON, replacing None with null."""
    return json.dumps(value, cls=CustomJSONEncoder)
