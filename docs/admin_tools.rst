Integration with django-admin-tools
===================================

If you are already using `django-admin-tools <https://github.com/django-admin-tools/django-admin-tools>`_ you can show all your Dashboards in Menu.

Create a ``custommenu`` if you haven't already.

.. code-block:: console

    python manage.py custommenu

It will generate ``menu.py``.  Set generated ``project.menu.CustomMenu`` as ``ADMIN_TOOLS_MENU`` in ``settings.py``.

.. code-block:: python
   
   # project/settings.py

   ADMIN_TOOLS_MENU = 'project.menu.CustomMenu'

Add ``ControlCenterMenu`` instance as menu childern in ``CustomMenu.__init__`` method as shown below.

.. code-block:: python

   # project/menu.py
   
       def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            ControlCenterMenu(), # as shown here
            items.Bookmarks(),
            items.AppList(
                _('Applications'),
                exclude=('django.contrib.*',)
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',)
            )
        ]

This should show ``Control Center`` menu with all your Dashboards in your admin.

You can read more about ``custommenu`` `here <https://django-admin-tools.readthedocs.io/en/latest/customization.html#customizing-the-navigation-menu>`_.