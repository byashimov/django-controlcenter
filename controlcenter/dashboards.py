import collections

from django.core.urlresolvers import reverse
from django.forms.widgets import MediaDefiningClass
from django.utils import six

from . import app_settings
from .base import BaseModel
from .widgets import Group

__all__ = ['Dashboard']


class Dashboard(six.with_metaclass(MediaDefiningClass, BaseModel)):
    pk = None
    widgets = ()

    class Media:
        css = {
            'all': [
                ('controlcenter/css/chartist-{}-colors.css'
                 .format(app_settings.CHARTIST_COLORS)),
                'controlcenter/css/chartist.css',
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

    def __init__(self, pk=None):
        super(Dashboard, self).__init__()
        self.pk = self.id = pk

    def get_absolute_url(self):
        return reverse('controlcenter:dashboard', kwargs={'pk': self.pk})

    def get_widgets(self, request, **options):
        # TODO: permission check
        for item in self.widgets:
            if isinstance(item, collections.Sequence):
                group = Group() + item
            else:
                group = Group([item])

            widgets = (x(request, **options) for x in group)
            new_group = Group(widgets, group.attrs, group.width, group.height)
            yield new_group
