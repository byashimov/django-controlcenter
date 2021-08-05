import collections
from typing import List, Tuple

from django.forms.widgets import MediaDefiningClass
from django.http.request import HttpRequest
from django.urls import reverse

from . import app_settings
from .base import BaseModel
from .widgets import BaseWidget
from pysilly_dj_dashboard.controlcenter import widgets


class Dashboard(BaseModel, metaclass=MediaDefiningClass):
    pk = None
    widgets: Tuple[BaseWidget] = ()

    class Media:
        css = {
            'all': [
                'controlcenter/css/chartist.css',
                # This must follow chartist.css to override correctly:
                ('controlcenter/css/chartist-{}-colors.css'
                 .format(app_settings.CHARTIST_COLORS)),
                'controlcenter/css/all.css',
            ]
        }
        js = (
            'controlcenter/js/masonry.pkgd.min.js',
            'controlcenter/js/chartist/chartist.min.js',
            'controlcenter/js/chartist/chartist-plugin-pointlabels.min.js',
            'controlcenter/js/sortable.min.js',
            'controlcenter/js/scripts.js',
        )

    def __init__(self, pk):
        super(Dashboard, self).__init__()
        self.pk = self.id = pk

    def get_title(self):
        return self.title

    def dispatch_request(self, request: HttpRequest):
        self.request = request

    def get_absolute_url(self):
        return reverse('controlcenter:dashboard', kwargs={'pk': self.pk})

    def get_widget_extra_options(self, request, **kwargs) -> dict:
        return kwargs

    def get_widgets(self, request, **options) -> List[BaseWidget]:
        """ Using `self.widgets`, init each class and set size bases on number of elements. """

        if type(self.widgets[0]) in (list, tuple):
            widgets = []
            for g in self.widgets:
                ws = []
                width = int(12 / len(g))
                for w in g:
                    ws.append(w(request, width=width, **self.get_widget_extra_options(request, **options)))

                widgets.append(ws)

            return widgets
        else:
            width = int(12 / len(self.widgets))

            return [[w(request, width=width, **self.get_widget_extra_options(request, **options)) for w in self.widgets]]            
