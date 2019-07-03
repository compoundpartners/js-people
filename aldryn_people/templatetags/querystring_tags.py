from __future__ import unicode_literals

from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def querystring_add(context, add_key, add_value):
    request = context["request"]
    qs = request.GET.copy()
    qs[add_key] = add_value

    return "&".join(["{}={}".format(key, value) for key, value in qs.items()])

@register.simple_tag(takes_context=True)
def querystring_remove(context, remove_key):
    request = context["request"]
    qs = {}
    for key, value in request.GET.items():
        if not key == remove_key:
            qs[key] = value

    return "&".join(["{}={}".format(key, value) for key, value in qs.items()])

@register.simple_tag(takes_context=True)
def display_choice(context, field):
    value = field.value() or ''
    if value and hasattr(field.field, 'choices'):
        value = dict(field.field.choices).get(field.value())
        if not value:
            try:
                value = dict(field.field.choices).get(int(field.value()))
            except:
                pass

    return value

@register.simple_tag
def to_list(*args):
    return args

@register.filter
def if_value(values):
    return [value for value in values if hasattr(value, 'value') and value.value()]
