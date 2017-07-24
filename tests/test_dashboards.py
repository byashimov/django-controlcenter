from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from controlcenter import widgets

from . import TestCase


@override_settings(CONTROLCENTER_DASHBOARDS=())
class A_DashboardTest(TestCase):
    # Must be first
    # 'cause @override_settings doesn't override settings well :(

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'superuser@example.com', 'superpassword')
        self.user = User.objects.create_user(
            'user', 'user@example.com', 'password')

    def test_no_dashboard_found(self):
        self.client.login(username='superuser', password='superpassword')
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(reverse('controlcenter:dashboard',
                                    kwargs={'pk': 0}))


class B_DashboardTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'superuser@example.com', 'superpassword')
        self.user = User.objects.create_user(
            'user', 'user@example.com', 'password')

    @override_settings(
        ROOT_URLCONF='urls',
        CONTROLCENTER_DASHBOARDS=('dashboards.EmptyDashboard',))
    def test_empty_dashboard(self):
        self.client.login(username='superuser', password='superpassword')

        # I wish I could cache urls, but reverse_lazy fails with py34 & 1.8
        # https://code.djangoproject.com/ticket/25424
        url_0 = reverse('controlcenter:dashboard', kwargs={'pk': 0})
        response_0 = self.client.get(url_0)

        # Status code test
        self.assertEqual(response_0.status_code, 200)

        # Widgets test
        # It's empty, remember?
        # We don't check context, because `get_widgets` returns iterator
        # and it's empty now
        dashboard = response_0.context['dashboard']
        with self.assertRaises(StopIteration):
            next(dashboard.get_widgets(request=None))

        # Absolute url test
        self.assertEqual(dashboard.get_absolute_url(), url_0)

        # Non-exists dashboard test
        url_1 = reverse('controlcenter:dashboard', kwargs={'pk': 1})
        response_1 = self.client.get(url_1)
        self.assertEqual(response_1.status_code, 404)

    @override_settings(
        ROOT_URLCONF='test_urls',
        CONTROLCENTER_DASHBOARDS=('dashboards.EmptyDashboard',
                                  'dashboards.NonEmptyDashboard'))
    def test_regular_dashboard(self):
        url = reverse('controlcenter:dashboard', kwargs={'pk': 1})
        # Non-staff fails
        self.client.login(username='user', password='password')
        response = self.client.get(url)
        self.assertRedirects(response,
                             '{}?next={}'.format(reverse('admin:login'),
                                                 url))
        # Staff proceed
        self.client.login(username='superuser', password='superpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        dashboard = response.context['dashboard']
        self.assertEqual(dashboard.get_absolute_url(), url)

        # It's not empty
        self.assertIsInstance(next(dashboard.get_widgets(request=None)),
                              widgets.Group)

    @override_settings(
        ROOT_URLCONF='test_urls',
        CONTROLCENTER_DASHBOARDS={'empty': 'dashboards.EmptyDashboard',
                                  'non-empty': 'dashboards.NonEmptyDashboard'})
    def test_slug_dashboard(self):
        url = reverse('controlcenter:dashboard-slug', kwargs={'slug': 'non-empty'})
        # Staff proceed
        from django.conf import settings
        print(settings.CONTROLCENTER_DASHBOARDS)
        import controlcenter
        print(controlcenter.app_settings.DASHBOARDS)
        self.client.login(username='superuser', password='superpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_multiple_dashboards(self):
        self.client.login(username='superuser', password='superpassword')
        dashboards = ['dashboards.NonEmptyDashboard' for i in range(30)]
        with self.settings(ROOT_URLCONF='test_urls',
                           CONTROLCENTER_DASHBOARDS=dashboards):
            for i, path in enumerate(dashboards):
                url = reverse('controlcenter:dashboard', kwargs={'pk': i})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
