from collections.abc import Sequence
import itertools
import os
from abc import ABCMeta

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from ..base import BaseModel

__all__ = ['Group', 'ItemList', 'Widget', 'SMALL', 'MEDIUM', 'LARGE',
           'LARGER', 'LARGEST', 'FULL']


# Actually we don't need all that sizes
# but should have a grid for Masonry
# so I'm going to leave the most helpful ones

SMALL = 1    # 25%  or  [x] + [x] + [x] + [x]
MEDIUM = 2   # 33%  or  [ x ] + [ x ] + [ x ]
LARGE = 3    # 50%  or  [   x   ] + [   x   ]
LARGER = 4   # 66%  or  [     x     ] + [ x ]
LARGEST = 5  # 75%  or  [      x      ] + [x]
FULL = 6     # 100% or  [         x         ]


class WidgetMeta(ABCMeta):
    # Makes certain methods cached
    CACHED_ATTRS = (
        # values for charts and itemlists
        'values',
    )

    def __new__(mcs, name, bases, attrs):
        # We can't use it on __init__ because
        # cached_property fires on property's __get__
        for attr in mcs.CACHED_ATTRS:
            if attr in attrs:
                attrs[attr] = cached_property(attrs[attr])
        return super(WidgetMeta, mcs).__new__(mcs, name, bases, attrs)


class BaseWidget(BaseModel, metaclass=WidgetMeta):
    title = None
    model = None
    queryset = None
    changelist_url = None
    cache_timeout = None
    template_name = None
    template_name_prefix = None
    limit_to = None
    width = None
    height = None

    def __init__(self, request, **options):
        super(BaseWidget, self).__init__()
        self.request = request
        self.init_options = options

    def get_template_name(self):
        assert self.template_name, (
            '{}.template_name is not defined.'.format(self))
        return os.path.join(self.template_name_prefix.rstrip(os.sep),
                            self.template_name.lstrip(os.sep))

    def get_queryset(self):
        # Copied from django.views.generic.detail
        # Boolean check will run queryset
        if self.queryset is not None:
            return self.queryset.all()
        elif self.model:
            return self.model._default_manager.all()
        raise ImproperlyConfigured(
            '{name} is missing a QuerySet. Define '
            '{name}.model, {name}.queryset or override '
            '{name}.get_queryset().'.format(name=self.__class__.__name__))

    def values(self):
        # If you put limit_to in get_queryset method
        # using of super().get_queryset() will not make any sense
        # because the queryset will be sliced
        queryset = self.get_queryset()
        if self.limit_to:
            return queryset[:self.limit_to]
        return queryset


class Group(Sequence):
    def __init__(self, widgets=None, attrs=None, width=None, height=None):
        self.widgets = tuple(widgets or ())
        self.attrs = (attrs or {}).copy()
        self.width, self.height = width, height

    def __repr__(self):
        return '<Group of widgets: {}>'.format(self.widgets)

    def __len__(self):
        return len(self.widgets)

    def __getitem__(self, index):
        return self.widgets[index]

    def __add__(self, other):
        widgets = itertools.chain(self, other)
        width = getattr(other, 'width', self.width)
        height = getattr(other, 'height', self.height)
        attrs = self.attrs.copy()
        other_attrs = getattr(other, 'attrs', None)
        if other_attrs:
            attrs.update(other_attrs)
        return Group(widgets, attrs, width, height)

    def get_id(self):
        return self.attrs.get('id', '_and_'.join(x.slug for x in self))

    def get_class(self):
        return self.attrs.get('class', '')

    def get_attrs(self):
        return {key: value for key, value
                in self.attrs.items()
                if key not in ('id', 'class')}

    def _get_size(self, size):
        value = getattr(self, size, None)
        if value is not None:
            return value
        elif self.widgets:
            # py3 hooks
            return max(getattr(x, size, None) or 0 for x in self) or None

    def get_width(self):
        return self._get_size('width')

    def get_height(self):
        return self._get_size('height')


class Widget(BaseWidget):
    limit_to = 10  # It's always a good reason to limit queryset
    width = MEDIUM
    template_name_prefix = 'controlcenter/widgets'


class ItemList(Widget):
    list_display = None
    list_display_links = None
    template_name = 'itemlist.html'
    empty_message = 'No items to display'
    sortable = False
