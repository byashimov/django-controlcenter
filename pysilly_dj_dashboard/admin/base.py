from typing import Dict, List, Optional, Tuple, Type, Union

from django.contrib import admin
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe

from pysilly_dj.admin import SillyMixin

from pysilly_dj_dashboard.admin.actions import TopAction


class DashboardModelAdmin(admin.ModelAdmin):
    top_actions: Union[Tuple[Type[TopAction]], List[Type[TopAction]]] = []

    def get_top_actions(self, request: HttpRequest) -> List[TopAction]:
        return [action(request) for action in self.top_actions]

    def changelist_view(self, request: HttpRequest, extra_context: Optional[Dict[str, str]] = {}) -> TemplateResponse:
        extra_context['top_actions'] = self.get_top_actions(request)
        return super().changelist_view(request, extra_context)


class DashboardSillyModelAdmin(SillyMixin, DashboardModelAdmin):
    pass
