# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from aldryn_people.views import (
    DownloadVcardView,
    GroupDetailView,
    GroupListView,
    PersonDetailView,
    SearchView,
    IndexView,
)
from .constants import (
    URL_PREFIX,
    SHOW_GROUP_LIST_VIEW,
    ALDRYN_PEOPLE_HIDE_GROUPS,
)

urlpatterns = [
    url(r'^search/$',
        SearchView.as_view(), name='search'),

    url(r'^(?P<pk>[0-9]+)/$',
        PersonDetailView.as_view(), name='person-detail'),
    url(r'^(?P<slug>[A-Za-z0-9_\-]+)/$',
        PersonDetailView.as_view(), name='person-detail'),

    url(r'^(?P<pk>[0-9]+)/download/$',
        DownloadVcardView.as_view(), name='download_vcard'),
    url(r'^(?P<slug>[A-Za-z0-9_\-]+)/download/$',
        DownloadVcardView.as_view(), name='download_vcard'),

]
if not ALDRYN_PEOPLE_HIDE_GROUPS:
    urlpatterns += [
        url(r'^group/(?P<pk>[0-9]+)/$',
            GroupDetailView.as_view(), name='group-detail'),
        url(r'^group/(?P<slug>[A-Za-z0-9_\-]+)/$',
            GroupDetailView.as_view(), name='group-detail'),
    ]
if SHOW_GROUP_LIST_VIEW and not ALDRYN_PEOPLE_HIDE_GROUPS:
    urlpatterns.append(url(r'^$',
        GroupListView.as_view(), name='group-list')
    )
else:
    urlpatterns.append(url(r'^$',
        SearchView.as_view(), name='list')
    )

if URL_PREFIX:
    URL_PREFIX += '/'
    extra_patterns = urlpatterns
    urlpatterns = [
        url(r'^$', IndexView.as_view(), name='index'),
        url(URL_PREFIX, include(extra_patterns))
    ]
