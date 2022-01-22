from django.contrib import admin

try:
    from django.urls import path
except ImportError:
    from django.conf.urls import url as path

from controlcenter.views import controlcenter


urlpatterns = [
    path('admin/dashboard/', controlcenter.urls),
    path('admin/', admin.site.urls),
]
