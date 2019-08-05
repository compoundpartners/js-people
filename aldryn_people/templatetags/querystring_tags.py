from __future__ import unicode_literals

from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def querystring_add(context, *args, **kwargs):
    request = context["request"]
    qs = request.GET.copy()
    if len(args) == 2:
        qs[args[0]] = args[1]
    for key, value in kwargs.items():
        qs[key] = value

    return "&".join(["{}={}".format(key, value) for key, value in qs.items()])

@register.simple_tag(takes_context=True)
def querystring_remove(context, *args):
    request = context["request"]
    qs = request.GET.copy()
    for key, value in request.GET.items():
        for remove_key in args:
            if key == remove_key and key in qs:
                del qs[key]

    return "&".join(["{}={}".format(key, value) for key, value in qs.items()])

@register.simple_tag(takes_context=True)
def display_choice(context, field):
    value = field.value() or '' if field else ''
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
    return [value for value in values if value and hasattr(value, 'value') and value.value()]
