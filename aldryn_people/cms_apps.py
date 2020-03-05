# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from aldryn_apphooks_config.app_base import CMSConfigApp
from .constants import ALDRYN_PEOPLE_HIDE_GROUPS
from . import DEFAULT_APP_NAMESPACE
from . import views
from . import models

if ALDRYN_PEOPLE_HIDE_GROUPS:
    class PeopleApp(CMSApp):
        name = _('People')
        app_name = DEFAULT_APP_NAMESPACE
        urls = ['aldryn_people.urls']  # COMPAT: CMS3.2

        def get_urls(self, *args, **kwargs):
            return self.urls
    apphook_pool.register(PeopleApp)

else:
    @apphook_pool.register
    class PeopleApp(CMSConfigApp):
        name = _('People')
        app_name = DEFAULT_APP_NAMESPACE
        app_config = models.Group
        urls = ['aldryn_people.urls']

        # NOTE: Please do not add a «menu» here, menu’s should only be added by at
        # the discretion of the operator.
        def get_configs(self):
            if not self.app_config.objects.filter(namespace=DEFAULT_APP_NAMESPACE).exists():
                conf = self.app_config(namespace=DEFAULT_APP_NAMESPACE, slug=DEFAULT_APP_NAMESPACE, name='All people')
                conf.save()
            return self.app_config.objects.all()

        def get_urls(self, page=None, language=None, **kwargs):
            if page and page.application_namespace == DEFAULT_APP_NAMESPACE:
                return self.urls
            return [url(r'^$', views.SearchView.as_view(), name='index'),]
