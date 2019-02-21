# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from aldryn_people.views import (
    LocationDetailView,
    LocationListView,
    DownloadVcardView,
    GroupDetailView,
    GroupListView,
    PersonDetailView,
    SearchView,
)

urlpatterns = [
    url(r'^search/$',
        SearchView.as_view(), name='search'),

    url(r'^location/(?P<pk>[0-9]+)/$',
        LocationDetailView.as_view(), name='location-detail'),
    url(r'^location/(?P<slug>[A-Za-z0-9_\-]+)/$',
        LocationDetailView.as_view(), name='location-detail'),
    url(r'^location/$',
        LocationListView.as_view(), name='location-list'),

    url(r'^group/(?P<pk>[0-9]+)/$',
        GroupDetailView.as_view(), name='group-detail'),
    url(r'^group/(?P<slug>[A-Za-z0-9_\-]+)/$',
        GroupDetailView.as_view(), name='group-detail'),

    url(r'^(?P<pk>[0-9]+)/$',
        PersonDetailView.as_view(), name='person-detail'),
    url(r'^(?P<slug>[A-Za-z0-9_\-]+)/$',
        PersonDetailView.as_view(), name='person-detail'),

    url(r'^(?P<pk>[0-9]+)/download/$',
        DownloadVcardView.as_view(), name='download_vcard'),
    url(r'^(?P<slug>[A-Za-z0-9_\-]+)/download/$',
        DownloadVcardView.as_view(), name='download_vcard'),

    url(r'^$',
        GroupListView.as_view(), name='group-list'),
]
