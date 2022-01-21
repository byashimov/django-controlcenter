import json
from collections.abc import Sequence, Mapping
from functools import partial

from django import template
from django.core.exceptions import FieldDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.base import ModelBase
from django.urls import NoReverseMatch, reverse
from django.utils.html import conditional_escape, format_html, mark_safe
from django.utils.http import urlencode

from .. import app_settings
from ..utils import indexonly

register = template.Library()


@register.filter
def jsonify(obj):
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))


@register.filter
def is_sequence(obj):
    return isinstance(obj, Sequence)


@register.simple_tag
def change_url(widget, obj):

    if not widget.model and not isinstance(obj, models.Model):
        # No chance to get model url
        return

    elif isinstance(obj, Mapping):
        pk = obj.get('pk', obj.get('id'))
        meta = widget.model._meta

    elif indexonly(obj):
        if not widget.list_display:
            # No chance to guess pk
            return
        # Excludes sharp tip zip keys and values
        keys = (k for k in widget.list_display if k != app_settings.SHARP)
        new_obj = {x: y for x, y in zip(keys, obj)}
        return change_url(widget, new_obj)
    else:
        pk = getattr(obj, 'pk', getattr(obj, 'id', None))
        if not isinstance(obj, models.Model):
            # Namedtuples and custom stuff
            meta = widget.model._meta
        elif getattr(obj, '_deferred', False):  # pragma: no cover
            # Deferred model
            meta = obj._meta.proxy_for_model._meta
        else:
            # Regular model or django 1.10 deferred
            meta = obj._meta

    if pk is None:
        # No chance to get item url
        return

    try:
        app_label, model_name = meta.app_label, meta.model_name
        return reverse('admin:{}_{}_change'.format(app_label, model_name),
                       args=[pk])
    except NoReverseMatch:
        return


@register.filter
def changelist_url(widget):
    obj = widget.changelist_url
    if not obj or isinstance(obj, str):
        # If it's None (empty) or provided a real url
        return obj
    elif isinstance(obj, (tuple, list)):
        # Model, {'key1': 'value1', 'key2':...}
        # Model, '?key1=value1&key2=value2...'
        model, params = obj
    else:
        # Just a Model
        model, params = obj, ''

    assert isinstance(model, ModelBase), (
        '{}.changelist_url should be a string or Model class, or a tuple '
        'with Model class as the first element.'.format(widget))
    assert isinstance(params, (dict, str)), (
        'Widget.changelist_url\'s second element should be a dict or '
        'a string.')

    if isinstance(params, dict):
        urlparams = urlencode(params, doseq=True)
    else:
        # It's a string
        urlparams = params

    if urlparams and not urlparams.startswith('?'):
        urlparams = '?' + urlparams

    changelist_url = reverse('admin:{}_{}_changelist'
                             .format(model._meta.app_label,
                                     model._meta.model_name))
    return changelist_url + urlparams


@register.simple_tag
def attrvalue(widget, obj, attrname):
    """
    Looks for an attribute value in widget.
    Then tries to get one from object (dict, sequence, model,
    namedtuple, whatever looks alike).
    """

    # Looks for a callable in widget
    attr = getattr(widget, attrname, None)
    if attr and callable(attr):
        value = attr(obj)
    elif isinstance(obj, Mapping):
        # Manager.values()
        value = obj.get(attrname)
    elif indexonly(obj):
        # Fist removes sharp from the list
        clone = list(widget.list_display or ())
        if app_settings.SHARP in clone:
            clone.remove(app_settings.SHARP)

        if attrname not in clone:
            value = None
        else:
            index = clone.index(attrname)
            try:
                # Obj might be shorter
                value = obj[index]
            except IndexError:
                value = None
    else:
        # Model, namedtuple, custom stuff
        attr = getattr(obj, attrname, None)
        value = attr() if callable(attr) else attr

    if value is None:
        # It's not found or the value is None
        return ''
    elif attr and getattr(attr, 'allow_tags', False):
        return mark_safe(value)
    else:
        # TODO: django 1.9 auto-escapes simple_tag
        return conditional_escape(value)


def _method_prop(obj, attrname, attrprop):
    """
    Returns property of callable object's attribute.
    """
    attr = getattr(obj, attrname, None)
    if attr and callable(attr):
        return getattr(attr, attrprop, None)


_method_label = partial(_method_prop, attrprop='short_description')


@register.filter
def attrlabel(widget, attrname):
    widget_prop = _method_label(widget, attrname)
    if widget_prop is not None:
        return widget_prop

    elif widget.model:
        model_prop = _method_label(widget.model, attrname)
        if model_prop is not None:
            # Allows to have empty description
            return model_prop

        if attrname == 'pk':
            fieldname = widget.model._meta.pk.name
        else:
            fieldname = attrname

        try:
            field = widget.model._meta.get_field(fieldname)
            return field.verbose_name
        except FieldDoesNotExist:
            pass
    return attrname


@register.simple_tag
def external_link(url, label=None):
    return format_html(
        '<a href="{href}" target="_blank" '
        'rel="noreferrer" rel="noopener">{label}</a>',
        href=url, label=label or url,
    )
