from collections import OrderedDict

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views.generic.base import TemplateView

from . import app_settings

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path



class ControlCenter(object):
    def __init__(self, name, view_class):
        self.name = name
        self.view_class = view_class

    def get_view(self):
        return self.view_class.as_view(controlcenter=self)

    def get_urls(self):
        urlpatterns = [
            re_path(r'^(?P<pk>\w+)/$', self.get_view(), name='dashboard'),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'controlcenter', self.name


class DashboardView(TemplateView):
    dashboard = None
    controlcenter = None
    template_name = 'controlcenter/dashboard.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = str(self.kwargs['pk'])
        try:
            self.dashboard = self.dashboards[pk]
        except KeyError:
            raise Http404('Dashboard not found.')
        return super(DashboardView, self).get(request, *args, **kwargs)

    @cached_property
    def dashboards(self):
        dashboards = OrderedDict()
        for slug, path in enumerate(app_settings.DASHBOARDS):
            if isinstance(path, (list, tuple)):
                slug, path = path
            pk = str(slug)
            klass = import_string(path)
            dashboards[pk] = klass(pk=pk)

        if not dashboards:
            raise ImproperlyConfigured('No dashboards found.')
        return dashboards

    def get_context_data(self, **kwargs):
        context = {
            'title': self.dashboard.title,
            'dashboard': self.dashboard,
            'dashboards': self.dashboards.values(),
            'groups': self.dashboard.get_widgets(self.request),
            'sharp': app_settings.SHARP,
        }

        # Admin context
        kwargs.update(admin.site.each_context(self.request))
        kwargs.update(context)
        return super(DashboardView, self).get_context_data(**kwargs)


controlcenter = ControlCenter('controlcenter', DashboardView)
