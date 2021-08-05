from django import template

register = template.Library()


@register.simple_tag
def get_model_icon(model):
    return 'bell'