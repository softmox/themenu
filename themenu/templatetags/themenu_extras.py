from django import template
# import settings
# from pyparsing import basestring

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, basestring):
        return text.startswith(starts)
    return False


@register.filter(name='get')
def get(obj, key):
    try:
        return obj[key]
    except KeyError:
        return settings.TEMPLATE_STRING_IF_INVALID
