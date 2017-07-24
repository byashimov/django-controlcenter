from django.test.utils import override_settings

from controlcenter import Dashboard, app_settings

from . import TestCase


class AppConfTest(TestCase):
    def test_setup(self):
        self.assertEqual(app_settings.__name__, 'controlcenter.app_settings')

    def test_defaults(self):
        # Settings.py should not contain any controlcenter setting
        self.assertEqual(app_settings.DASHBOARDS, [])
        self.assertEqual(app_settings.CHARTIST_COLORS, 'default')
        self.assertEqual(app_settings.SHARP, '#')

    @override_settings(
        CONTROLCENTER_CHARTIST_COLORS='google',
        CONTROLCENTER_DASHBOARDS=[Dashboard])
    def test_changes(self):
        self.assertEqual(app_settings.DASHBOARDS, [Dashboard])
        self.assertEqual(app_settings.CHARTIST_COLORS, 'google')

    @override_settings(
        CONTROLCENTER_DASHBOARDS={'default': Dashboard})
    def test_changes_with_slug(self):
        self.assertEqual(app_settings.DASHBOARDS, {'default': Dashboard})

    def test_unknown(self):
        with self.assertRaises(AttributeError):
            app_settings.DEBUG

    def test_monkeypatching(self):
        from django.conf import settings
        settings.CONTROLCENTER_CHARTIST_COLORS = 'monkey'
        self.assertEqual(app_settings.CHARTIST_COLORS, 'monkey')
