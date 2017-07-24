from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.generic.base import TemplateView

from . import app_settings


class ControlCenter(object):
    def __init__(self, view_class):
        self.view_class = view_class

    def get_dashboards(self):
        _dashboards = app_settings.DASHBOARDS
        if isinstance(_dashboards, dict):
            dashboards = {
                slug: import_string(klass)(pk=slug)
                for slug, klass in _dashboards.items()
            }
        else:
            klasses = map(import_string, app_settings.DASHBOARDS)
            dashboards = [klass(pk=pk) for pk, klass in enumerate(klasses)]
        if not dashboards:
            raise ImproperlyConfigured('No dashboards found.')
        return dashboards

    def get_view(self):
        dashboards = self.get_dashboards()
        return self.view_class.as_view(dashboards=dashboards)

    def get_urls(self):
        urlpatterns = [
            url(r'^(?P<pk>\d+)/$', self.get_view(), name='dashboard'),
            url(r'^(?P<slug>.+)/$', self.get_view(), name='dashboard-slug'),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'controlcenter', 'controlcenter'


class DashboardView(TemplateView):
    dashboards = NotImplemented
    template_name = 'controlcenter/dashboard.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if 'pk' in self.kwargs:
            pk = int(self.kwargs['pk'])
        elif 'slug' in self.kwargs:
            pk = self.kwargs['slug']
        try:
            self.dashboard = self.dashboards[pk]
        except (IndexError, KeyError):
            raise Http404('Dashboard not found.')
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'title': self.dashboard.title,
            'dashboard': self.dashboard,
            'dashboards': self.dashboards,
            'groups': self.dashboard.get_widgets(self.request),
            'sharp': app_settings.SHARP,
        }

        # Admin context
        kwargs.update(admin.site.each_context(self.request))
        kwargs.update(context)
        return super(DashboardView, self).get_context_data(**kwargs)


controlcenter = ControlCenter(view_class=DashboardView)
