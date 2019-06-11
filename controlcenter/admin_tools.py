from admin_tools.menu.items import MenuItem
from admin_tools.utils import AppListElementMixin
from django.conf import settings
from django.urls.base import reverse
from django.utils.safestring import mark_safe


class ControlCenterMenu(MenuItem, AppListElementMixin):
    title = "Control Center"

    def init_with_context(self, context):

        for pk, full_class_name in settings.CONTROLCENTER_DASHBOARDS:
            module_name = full_class_name.split(".")
            class_name = module_name.pop()

            from importlib import import_module
            _module = import_module(".".join(module_name))
            _class = getattr(_module, class_name)

            title = mark_safe(_class.title if _class.title else class_name)
            url = reverse("controlcenter:dashboard", args=(pk,))

            self.children.append(MenuItem(title=title, url=url))

        if not len(self.children):
            self.enabled = False

    def is_selected(self, request):
        return False
