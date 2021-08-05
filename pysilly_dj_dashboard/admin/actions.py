from typing import Optional
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class Action:
    _href: str = None
    _label: str = None

    def __init__(
        self,
        request: Optional[HttpRequest] = None,
        href: Optional[str] = None,
        label: Optional[str] = None
    ):
        self.request: HttpRequest = request
        self._href = href
        self._label = label

    def __str__(self):
        return self.render

    @property
    def html(self):
        return mark_safe(self.render)

    @property
    def render(self):
        return '<a href="{}">{}</a>'.format(
            self.href,
            self.label
        )

    @property
    def label(self) -> str:
        if self._label:
            return self._label

        return _(self.get_label())

    @property
    def href(self) -> str:
        if self._href:
            return self._href

        return self.get_href()

    def get_href(self) -> str:
        raise NotImplementedError

    def get_label(self) -> str:
        raise NotImplementedError


class TopAction(Action):
    pass