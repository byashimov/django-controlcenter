Welcome to django-controlcenter!
================================

Get all your project models on one single page with charts and whistles.

.. image:: https://cloud.githubusercontent.com/assets/1560043/14309295/b8c9aad0-fc05-11e5-96d0-44293d2d07ff.png
    :alt: django-controlcenter

Attention!
----------

Unfortunately, I have no time to add new features.
Please make PR if you need one:

- branch from master
- provide tests
- add docs
- update changelog

That's it.


Rationale
---------

Django-admin_ is a great tool to control your project activity: new orders, comments, replies, users, feedback -- everything is here. The only struggle is to switch between all those pages constantly just to check them out for new entries.

With django-controlcenter you can have all of your models on one single page and build beautiful charts with Chartist.js_. Actually they don't even have to be a django models, get your data from wherever you want: RDBMS, NOSQL, text file or even from an external web-page, it doesn't matter.


Quickstart
----------

Install django-controlcenter:

.. code-block:: console

    pip install -U django-controlcenter

Create a dashboard file with unlimited number of widgets and dashboards:

.. code-block:: python

    from controlcenter import Dashboard, widgets
    from project.app.models import Model

    class ModelItemList(widgets.ItemList):
        model = Model
        list_display = ('pk', 'field')

    class MyDashboard(Dashboard):
        widgets = (
            ModelItemList,
        )

Update settings file:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'controlcenter',
        ...
    ]

    CONTROLCENTER_DASHBOARDS = (
        ('mydash', 'project.dashboards.MyDashboard'),
    )

Plug in urls:

.. code-block:: python

    from django.urls import path
    from django.contrib import admin
    from controlcenter.views import controlcenter

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('admin/dashboard/', controlcenter.urls),
        ...
    ]

Open ``/admin/dashboard/mydash/`` in browser.


Documentation
-------------

Check out the docs_ for more complete examples.


Compatibility
-------------

.. image:: https://travis-ci.org/byashimov/django-controlcenter.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/byashimov/django-controlcenter

.. image:: https://codecov.io/github/byashimov/django-controlcenter/coverage.svg?branch=master
    :alt: Codecov
    :target: https://codecov.io/github/byashimov/django-controlcenter?branch=master

Tested on py 3.5—3.10 and django 1—4.


Credits
-------

This project uses Chartist.js_, Masonry.js_ and Sortable.js_.


Changelog
---------

0.3.1
~~~~~

- Support django 4.0, python 3.10. Thanks to @mick88.
- Fixed LineChart example. Thanks to @virtosubogdan.

0.3.0
~~~~~

- Support django 3.0
- Python 3 only

0.2.9
~~~~~

- ``chartist-plugin-pointlabels`` temporary fix
- Added sorting triangles to ``ItemList``
- ``ItemList`` header is now always displayed regardless sortability
- Other misc improvements

Thanks to @minusf.

0.2.8
~~~~~

- Fixed ``key_value_list.html`` widget template syntax error.
- Fixed attribute typo ``widget.chartist.point_labels -> point_lables``.

Thanks to @minusf.

0.2.7
~~~~~

- New ``TimeSeriesChart`` widget. Thanks to @pjdelport.
- New "simple" widgets: ``ValueList`` and ``KeyValueList``. Thanks to @tonysyu.
- Bunch of fixes and improvements, thanks again to @pjdelport.


0.2.6
~~~~~

- Fixed navigation menu links, thanks to @editorgit

0.2.5
~~~~~

- It's now possible to use slugs for dashboards instead of those indexes in ``CONTROLCENTER_DASHBOARDS``.
  The old behaviour is supported too.

0.2.4
~~~~~

- It's compatible with django 1.8—2.1 now
- Custom app name can be passed to ``ControlCenter`` class

0.2.3
~~~~~
- Updated column grid, thanks to @pauloxnet.
- Grammar fixes, thanks to @danielquinn.
- It's should be possible now to use a custom dashboard view with a custom template.

0.2.2
~~~~~
- ``dashboard.html`` now extends ``admin/base_site.html`` instead of ``admin/base.html``
  in order to display *branding* block. Thanks to @chadgh.
- Updated ``jsonify`` tag filter, thanks to @k8n.

0.2.1
~~~~~
- Django 1.10 support. Tested in tox *only*.
- Updated the SingleBarChart example, thanks to @greeve.

0.2.0
~~~~~
- Unlimited dashboards support.
- Configuration constructor is moved to a separate project -- django-pkgconf_. It's a dependency now.

0.1.2
~~~~~
- Chart ``i`` series color fix. Thanks to @uncleNight.
- Docs. Finally.

0.1.1
~~~~~
- Better responsive experience.

0.1.0
~~~~~
- First public release.

.. _Chartist.js: http://gionkunz.github.io/chartist-js/
.. _Masonry.js:  http://masonry.desandro.com/
.. _Sortable.js: http://github.hubspot.com/sortable/docs/welcome/
.. _Django-admin: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
.. _django-pkgconf: https://github.com/byashimov/django-pkgconf
.. _docs: http://django-controlcenter.readthedocs.io/en/latest/
