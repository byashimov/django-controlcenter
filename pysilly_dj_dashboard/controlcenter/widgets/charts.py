from datetime import datetime, timedelta 
from typing import Dict, List, Optional, Tuple, Union

from django.utils.functional import cached_property
from ..utils import deepmerge
from .core import Widget, WidgetMeta


# Chart types
PIE, BAR, LINE = 'Pie', 'Bar', 'Line'


class Chartist(object):
    def __init__(self):
        self.options = {}

    def update(self, obj):
        for key in dir(obj):
            value = getattr(obj, key)
            if key == 'options':
                self.options = deepmerge(self.options, value)
            elif not key.startswith('__') and not callable(value):
                setattr(self, key, value)


class ChartMeta(WidgetMeta):
    CACHED_ATTRS = WidgetMeta.CACHED_ATTRS + (
        'labels',  # chart x-axis labels
        'series',  # chart y-axis values
        'legend',  # chart legend
    )

    def __new__(mcs, name, bases, attrs):
        # Saves defined configuration
        chartist = attrs.pop('Chartist', None)

        new_class = super(ChartMeta, mcs).__new__(mcs, name, bases, attrs)
        new_class.chartist = Chartist()

        # Copies parents options
        for base in bases:
            if hasattr(base, 'chartist'):
                new_class.chartist.update(base.chartist)

        # Overrides inherited stuff
        if chartist:
            new_class.chartist.update(chartist)
        return new_class


class Chart(Widget, metaclass=ChartMeta):
    template_name = 'chart.html'

    class Chartist:
        klass = LINE
        scale = 'octave'

    def legend(self):
        # Legend for chart
        return []

    def labels(self):
        # List of x-axis labels
        # Do not return generator!
        return []

    def series(self):
        # List of y-axis values
        # Do not return generator!
        return []


class LineChart(Chart):
    class Chartist:
        point_labels = True
        options = {
            # In common cases you need something last ordered by descending,
            # setting `reverseData` all the time is just annoying
            'reverseData': True,
            'axisY': {
                'onlyInteger': True,
            },
            'fullWidth': True,
        }


class TimeSeriesChart(Chart):
    class Chartist:
        point_labels = True
        options = {
            'axisY': {
                'onlyInteger': True,  # Same default as LineChart.
            },
        }
        time_series = True
        timestamp_options = {}


class BarChart(Chart):
    class Chartist:
        klass = BAR


class PieChart(Chart):
    class Chartist:
        klass = PIE


class SinglePieChart(PieChart):
    values_list = None

    def labels(self):
        return [x for x, y in self.values]

    def series(self):
        return [y for x, y in self.values]

    def values(self):
        assert self.values_list, ('Please define {0}.values_list '
                                  'or override {0}.values'.format(self))
        queryset = self.get_queryset().values_list(*self.values_list)
        if self.limit_to:
            return queryset[:self.limit_to]
        return queryset


class SingleBarChart(SinglePieChart, BarChart):
    class Chartist:
        options = {
            'distributeSeries': True
        }


class SingleLineChart(SinglePieChart, LineChart):
    def series(self):
        vals = super(SingleLineChart, self).series
        return [vals]


class LineOverTimeChart(LineChart):
    interval: int = 1
    interval_type: str = 'weeks'
    date_filter_key: str = 'created_at'
    date_spliter_key: str = '::'

    @property
    def queryset(self):
        raise NotImplementedError

    def get_start_date(self) -> Optional[datetime]:
        raise NotImplementedError

    def get_finish_date(self) -> Optional[datetime]:
        raise NotImplementedError

    def get_date_filter(self):
        return {
            '{}__gte'.format(self.date_filter_key): self.start_date,
            '{}__lte'.format(self.date_filter_key): self.finish_date
        }

    def get_queryset(self):
        return self.queryset.filter(**self.get_date_filter()).order_by(self.date_filter_key)

    def get_dict_data(self) -> Dict[str, int]:
        data = {}
        start_date = self.start_date - timedelta(**{self.interval_type: self.interval})

        while start_date < self.finish_date + timedelta(**{self.interval_type: self.interval}):
            _start_date = start_date + timedelta(**{self.interval_type: self.interval})

            if self.interval_type == 'days':
                data[start_date.date().isoformat()] = 0
            else:
                data['{}{}{}'.format(
                    start_date.date().isoformat(),
                    self.date_spliter_key,
                    _start_date.date().isoformat())
                ] = 0

            start_date = _start_date

        return data

    def format_data_to_series_and_labels(self, data: Dict[str, int]) -> Tuple[List[str], List[Union[int, float]]]:
        return (
            [v for _, v in data.items()],
            [k for k in data.keys()]
        )

    @cached_property
    def start_date(self) -> datetime:
        return self.get_start_date()

    @cached_property
    def finish_date(self) -> datetime:
        return self.get_finish_date()

    @cached_property
    def series_and_labels(self):
        if not(self.start_date and self.finish_date):
            return

        qs = list(self.get_queryset())
        data = self.get_dict_data()

        for key, _ in data.items():
            if self.interval_type == 'days':
                start_date = datetime.strptime(key, "%Y-%m-%d")
            else:
                start_date, finish_date = key.split(self.date_spliter_key)
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                finish_date = datetime.strptime(finish_date, "%Y-%m-%d")
                finish_date = finish_date.date()

            start_date = start_date.date()

            for index, item in enumerate(qs):
                item_date = getattr(item, self.date_filter_key).date()

                if self.interval_type == 'days':
                    if item_date >= start_date and item_date <= start_date:
                        data[key] += 1
                        qs.pop(index)
                else:
                    if item_date >= start_date and item_date <= finish_date:
                        data[key] += 1
                        qs.pop(index)
        
        return self.format_data_to_series_and_labels(data)


    def series(self) -> List[int]:
        return [self.series_and_labels[0]]

    def labels(self) -> List[str]:
        return self.series_and_labels[1]