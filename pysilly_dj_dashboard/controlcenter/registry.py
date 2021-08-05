import functools
from typing import List

from pysilly_dj_dashboard.controlcenter.dashboards import Dashboard


class DashboardRegistry:
    dashboards: List[Dashboard] = {}
    home_dashboard_pk: Dashboard = None

    @classmethod
    def register(cls, dashboard_pk: str, set_as_home: bool = False):
        @functools.wraps(cls)
        def wrapper(dashboard_clazz, *args, **kwargs):
            cls.dashboards[dashboard_pk] = dashboard_clazz

            if set_as_home and not cls.home_dashboard_pk:
                cls.home_dashboard_pk = dashboard_pk

            return cls
        return wrapper
