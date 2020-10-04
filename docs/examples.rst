Examples
========

Lets say we have an app with this models:

.. code-block:: python

    from django.db import models


    class Pizza(models.Model):
        name = models.CharField(max_length=100, unique=True)

        def __str__(self):
            return self.name


    class Restaurant(models.Model):
        name = models.CharField(max_length=100, unique=True)
        menu = models.ManyToManyField(Pizza, related_name='restaurants')

        def __str__(self):
            return self.name


    class Order(models.Model):
        created = models.DateTimeField(auto_now_add=True)
        restaurant = models.ForeignKey(Restaurant, related_name='orders', on_delete=models.CASCADE)
        pizza = models.ForeignKey(Pizza, related_name='orders', on_delete=models.CASCADE)

I'm going to put all imports in here just to not mess up the code blocks:

.. code-block:: python

    # project/dashboards.py

    import datetime

    from django.db.models import Count
    from django.utils import timezone
    from controlcenter import Dashboard, widgets
    from .pizza.models import Order, Pizza, Restaurant


Scrollable ItemList with fixed height
------------------------------------

Set ``height`` to make ``ItemList`` scrollable.

.. code-block:: python

    class MenuWidget(widgets.ItemList):
        # This widget displays a list of pizzas ordered today
        # in the restaurant
        title = 'Ciao today orders'
        model = Pizza
        list_display = ['name', 'ocount']
        list_display_links = ['name']

        # By default ItemList limits queryset to 10 items, but we need all of them
        limit_to = None

        # Sets widget's max-height to 300 px and makes it scrollable
        height = 300

        def get_queryset(self):
            restaurant = super(MenuWidget, self).get_queryset().get()
            today = timezone.now().date()
            return (restaurant.menu
                              .filter(orders__created__gte=today, name='ciao')
                              .order_by('-ocount')
                              .annotate(ocount=Count('orders')))


Sortable and numerated ItemList
-------------------------------

To make ``ItemList`` numerate rows simply add ``SHARP`` sign to ``list_display``. To make it sortable set ``sortable = True``. Remember: it's client-side sorting.

.. code-block:: python

    from controlcenter import app_settings
    from django.utils.timesince import timesince


    class LatestOrdersWidget(widgets.ItemList):
        # Displays latest 20 orders in the the restaurant
        title = 'Ciao latest orders'
        model = Order
        queryset = (model.objects
                         .select_related('pizza')
                         .filter(created__gte=timezone.now().date(),
                                 name='ciao')
                         .order_by('pk'))
        # This is the magic
        list_display = [app_settings.SHARP, 'pk', 'pizza', 'ago']

        # If list_display_links is not defined, first column to be linked
        list_display_links = ['pk']

        # Makes list sortable
        sortable = True

        # Shows last 20
        limit_to = 20

        # Display time since instead of date.__str__
        def ago(self, obj):
            return timesince(obj.created)


Building multiple widgets with meta-class
-----------------------------------------

Lets assume we have not filtered previous widgets querysets to Ciao restaurant. Then we can create widgets in a loop.

.. code-block:: python

    from controlcenter.widgets.core import WidgetMeta

    RESTAURANTS = [
        'Mama',
        'Ciao',
        'Sicilia',
    ]

    # Metaclass arguments are: class name, base, properties.
    menu_widgets = [WidgetMeta('{}MenuWidget'.format(name),
                               (MenuWidget,),
                               {'queryset': Restaurant.objects.filter(name=name),
                                # Adds human readable dashboard title
                                'title': name + ' menu',
                                # A link to model admin page
                                'changelist_url': (
                                     Pizza, {'restaurants__name__exact': name})})
                    for name in RESTAURANTS]

    latest_orders_widget = [WidgetMeta(
                               '{}LatestOrders'.format(name),
                               (LatestOrdersWidget,),
                               {'queryset': (LatestOrdersWidget
                                                .queryset
                                                .filter(restaurant__name=name)),
                                'title': name + ' orders',
                                'changelist_url': (
                                     Order, {'restaurant__name__exact': name})})
                            for name in RESTAURANTS]


Displaying series in legend
---------------------------

.. code-block:: python

    class RestaurantSingleBarChart(widgets.SingleBarChart):
        # Displays score of each restaurant.
        title = 'Most popular restaurant'
        model = Restaurant

        class Chartist:
            options = {
                # Displays only integer values on y-axis
                'axisY': {
                    'onlyInteger': True
                },
                'axisX': {
                    'onlyInteger': True
                },
                # Visual tuning
                'chartPadding': {
                    'top': 24,
                    'right': 0,
                    'bottom': 0,
                    'left': 0,
                }
            }

        def legend(self):
            # Duplicates series in legend, because Chartist.js
            # doesn't display values on bars
            return self.series

        def values(self):
            # Returns pairs of restaurant names and order count.
            queryset = self.get_queryset()
            return (queryset.values_list('name')
                            .annotate(baked=Count('orders'))
                            .order_by('-baked')[:self.limit_to])


LineChart widget with multiple series
-------------------------------------

.. code-block:: python

    from collections import defaultdict

    class OrderLineChart(widgets.LineChart):
        # Displays orders dynamic for last 7 days
        title = 'Orders this week'
        model = Order
        limit_to = 7
        # Lets make it bigger
        width = widgets.LARGER

        class Chartist:
            # Visual tuning
            options = {
                'axisX': {
                    'labelOffset': {
                        'x': -24,
                        'y': 0
                    },
                },
                'chartPadding': {
                    'top': 24,
                    'right': 24,
                }
            }

        def legend(self):
            # Displays restaurant names in legend
            return RESTAURANTS

        def labels(self):
            # Days on x-axis
            today = timezone.now().date()
            labels = [(today - datetime.timedelta(days=x)).strftime('%d.%m')
                      for x in range(self.limit_to)]
            return labels

        def series(self):
            # Some dates might not exist in database (no orders are made that
            # day), makes sure the chart will get valid values.
            series = []
            # Since Chartist reverseData is True by default in LineChart,
            # series order should also be reversed
            for restaurant in reversed(self.legend):
                # Sets zero if date not found
                item = self.values.get(restaurant, {})
                series.append([item.get(label, 0) for label in self.labels])
            return series

        def values(self):
            # Increases limit_to by multiplying it on restaurant quantity
            limit_to = self.limit_to * len(self.legend)
            queryset = self.get_queryset()
            # This is how `GROUP BY` can be made in django by two fields:
            # restaurant name and date.
            # Ordered.created is datetime type but we need to group by days,
            # here we use `DATE` function (sqlite3) to convert values to
            # date type.
            # We have to sort by the same field or it won't work
            # with django ORM.
            queryset = (queryset.extra({'baked':
                                        'DATE(created)'})
                                .select_related('restaurant')
                                .values_list('restaurant__name', 'baked')
                                .order_by('-baked')
                                .annotate(ocount=Count('pk'))[:limit_to])

            # The key is restaurant name and the value is a dictionary of
            # date:order_count pair.
            values = defaultdict(dict)
            for restaurant, date, count in queryset:
                # `DATE` returns `YYYY-MM-DD` string.
                # But we want `DD-MM`
                day_month = '{2}.{1}'.format(*date.split('-'))
                values[restaurant][day_month] = count
            return values


Simple data widgets
-------------------

There's also support for displaying plain python data as widgets.
Currently, two base classes are provided for rendering data:
`ValueList`, which handles list data, and `KeyValueList`, which
handles dictionary data. Each value (or key) can be a simple string
or it can be dictionaries or objects with the following attributes:

- ``label``: Label displayed in the widget
- ``url``: If present, the label become a hyperlink to this url
- ``help_text``: If present, display additional text accompanying label

If you want to specify these fields for a dictionary key, you'll need
use ``DataItem`` from ``controlcenter.widgets.contrib.simple``, since you
can't use a dictionary as a key to a dictionary because it's not hashable.

.. code-block:: python

    from controlcenter.widgets.contrib import simple as widgets
    from controlcenter.widgets.contrib.simple DataItem
    from django.conf import settings


    class DebuggingEndpointsWidget(widgets.ValueList):
        title = 'Debugging Endpoints'
        subtitle = 'Links for debugging application issues'

        def get_data(self):
            return [
                # Plain text displays as a row in the widget.
                'Not really sure why you would want plain text here',
                # Dictionary defining a display label and a url.
                {'label': 'Datadog Dashboard', 'url': 'https://example.com'},
                # `DataItem` can be used as an alternative to dictionaries.
                DataItem(label='Healthcheck', url='https://example.com',
                         help_text='Healthcheck report for external dependencies'),
            ]


    class AppInfoWidget(widgets.KeyValueList):
        title = 'App info'

        def get_data(self):
            return {
                # A simple key-value pair
                'Language code': settings.LANGUAGE_CODE,
                # A dictionary value can be used to display a link
                'Default timezone': {
                    'label': settings.TIME_ZONE,
                    'url': 'https://docs.djangoproject.com/en/2.1/topics/i18n/timezones/',
                },
                # To display a key with a link, you must use `DataItem` instead
                # of a dictionary, since keys must be hashable.
                DataItem(
                    label='Debug on',
                    url='https://docs.djangoproject.com/en/2.1/ref/settings/#debug'
                ): settings.DEBUG,
            }
