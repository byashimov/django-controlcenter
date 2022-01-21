from collections.abc import Sequence

from django.forms.widgets import MediaDefiningClass
from django.urls import reverse

from . import app_settings
from .base import BaseModel
from .widgets import Group

__all__ = ['Dashboard']


class Dashboard(BaseModel, metaclass=MediaDefiningClass):
    pk = None
    widgets = ()

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

    def get_absolute_url(self):
        return reverse('controlcenter:dashboard', kwargs={'pk': self.pk})

    def get_widgets(self, request, **options):
        # TODO: permission check
        for item in self.widgets:
            if isinstance(item, Sequence):
                group = Group() + item
            else:
                group = Group([item])

            widgets = (x(request, **options) for x in group)
            new_group = Group(widgets, group.attrs, group.width, group.height)
            yield new_group
