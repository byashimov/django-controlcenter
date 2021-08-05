"""
Generic widgets for `django-controlcenter` dashboards that don't require
model data.
"""

from abc import abstractmethod
from collections import namedtuple

from .. import core

__all__ = ['BaseSimpleWidget', 'ValueList', 'KeyValueList', 'DataItem']


DataItem = namedtuple('DataItem', 'label url help_text')
DataItem.__new__.__defaults__ = ('', '', '')


class BaseSimpleWidget(core.BaseWidget):
    width = core.MEDIUM
    template_name_prefix = 'controlcenter/widgets/contrib'

    @abstractmethod
    def get_data(self):
        """
        Should be implemented in a subclass.
        """


class ValueList(BaseSimpleWidget):
    template_name = 'value_list.html'
    value_column_label = None
    sortable = False

    def items(self):
        return self.get_data()


class KeyValueList(BaseSimpleWidget):
    template_name = 'key_value_list.html'
    key_column_label = None
    value_column_label = None
    sortable = False

    def items(self):
        return self.get_data().items()
