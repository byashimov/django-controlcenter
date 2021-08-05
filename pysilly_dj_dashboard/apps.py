from django.contrib.admin.apps import AdminConfig


class PysillyDjDashboardAdminConfig(AdminConfig):
    default_site = 'pysilly_dj_dashboard.admin.site.PySillyAdmin'
