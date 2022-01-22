from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings

from controlcenter import widgets

from . import TestCase

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


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
        CONTROLCENTER_DASHBOARDS=[('empty', 'dashboards.EmptyDashboard')])
    def test_empty_dashboard(self):
        self.client.login(username='superuser', password='superpassword')

        # I wish I could cache urls, but reverse_lazy fails with py34 & 1.8
        # https://code.djangoproject.com/ticket/25424
        url_0 = reverse('controlcenter:dashboard', kwargs={'pk': 'empty'})
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

    def test_multiple_dashboards(self):
        self.client.login(username='superuser', password='superpassword')
        dashboards = ['dashboards.NonEmptyDashboard' for i in range(30)]
        with self.settings(CONTROLCENTER_DASHBOARDS=dashboards):
            for i, path in enumerate(dashboards):
                url = reverse('controlcenter:dashboard', kwargs={'pk': i})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_navigation_links(self):
        self.client.login(username='superuser', password='superpassword')
        dashboards = (
            ('foo', 'dashboards.NonEmptyDashboard'),
            ('bar', 'dashboards.NonEmptyDashboard'),
            ('baz', 'dashboards.NonEmptyDashboard'),
        )
        with self.settings(CONTROLCENTER_DASHBOARDS=dashboards):
            response = self.client.get('/admin/dashboard/foo/')
            self.assertEqual(response.status_code, 200)
            expected = (
                '<div class="controlcenter__nav__item '
                'controlcenter__nav__item--active">Non empty dashboard</div>',
                '<a class="controlcenter__nav__item" '
                'href="/admin/dashboard/bar/">Non empty dashboard</a>',
                '<a class="controlcenter__nav__item" '
                'href="/admin/dashboard/baz/">Non empty dashboard</a>',
            )

            content = response.content.decode()
            for chunk in expected:
                # fixme: use subtest someday
                self.assertInHTML(chunk, content)
