import collections
import itertools
import os
from abc import ABCMeta
from typing import Any, AnyStr, Dict, List, Optional, Union

from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.utils.functional import cached_property
from django.utils.html import mark_safe
from django.urls import reverse

from ..base import BaseModel


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
    queryset: QuerySet = None
    changelist_url = None
    cache_timeout = None
    template_name = None
    template_name_prefix = None
    limit_to = None
    width: int = None
    height = None

    def __init__(
        self,
        request,
        width: int = None,
        **options
    ):
        super(BaseWidget, self).__init__()
        self.width = width
        self.request = request
        self.init_options = options
        self.dispatch()

    def dispatch(self) -> None:
        return

    @property
    def has_footer(self) -> bool:
        return False

    @property
    def has_header(self) -> bool:
        return bool(self.header)

    @property
    def header(self) -> Optional[str]:
        return self.get_header()

    @property
    def footer(self) -> Optional[str]:
        return self.get_footer()

    @staticmethod
    def to_link(value: str, url: str):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                url,
                value
            )
        )

    def get_header(self) -> Optional[str]:
        return mark_safe('<h5> {} </h5>'.format(self.title))

    def get_footer(self) -> Optional[str]:
        return None

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


class StaticList(Widget):
    list_display = None
    list_display_links = None
    template_name = 'itemlist.html'
    empty_message = 'No items to display'
    sortable = False

    def get_values(self) -> Dict[str, Any]:
        raise NotImplementedError

    def values(self):
        return [[' '.join(k.split('_')).capitalize(), v] for k, v in self.get_values().items()]
