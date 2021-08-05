from typing import Any, Dict, Optional
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import admin
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.template.response import TemplateResponse

from pysilly_dj_dashboard.controlcenter.registry import DashboardRegistry


class PySillyAdmin(admin.AdminSite):
    def index(self, request: WSGIRequest, extra_context: Optional[Dict[str, Any]] = {}) -> TemplateResponse:
        if DashboardRegistry.home_dashboard_pk:
            return redirect(reverse('controlcenter:dashboard', kwargs={'pk': DashboardRegistry.home_dashboard_pk}))

        return super().index(request, extra_context=extra_context)

    @property
    def site_name(self):
        return getattr(settings, 'SITE_NAME', 'PySilly')

    @property
    def site_title(self):
        return 'Steve'

    @property
    def site_header(self):
        if hasattr(settings, 'SITE_HEADER'):
            return settings.SITE_HEADER

        return '{} administration'.format(self.site_name)

    @property
    def index_title(self):
        if hasattr(settings, 'INDEX_TITLE'):
            return settings.INDEX_TITLE

        return '{} dashboard'.format(self.site_name)
