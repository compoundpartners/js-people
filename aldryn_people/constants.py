# -*- coding: utf-8 -*-

from django.conf import settings

PEOPLE_PLUGIN_STYLES = getattr(
    settings,
    'PEOPLE_PLUGIN_STYLES',
    '',
)

ALDRYN_PEOPLE_USER_THRESHOLD = getattr(
    settings,
    'ALDRYN_PEOPLE_USER_THRESHOLD',
    50,
)

ALDRYN_PEOPLE_HIDE_FAX = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_FAX',
    0,
)
ALDRYN_PEOPLE_HIDE_WEBSITE = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_WEBSITE',
    0,
)
ALDRYN_PEOPLE_HIDE_FACEBOOK = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_FACEBOOK',
    0,
)
ALDRYN_PEOPLE_HIDE_TWITTER = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_TWITTER',
    0,
)
ALDRYN_PEOPLE_HIDE_LINKEDIN = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_LINKEDIN',
    0,
)
ALDRYN_PEOPLE_HIDE_GROUPS = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_GROUPS',
    0,
)
ALDRYN_PEOPLE_HIDE_GROUPS = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_USER',
    0,
)
ALDRYN_PEOPLE_SHOW_SECONDARY_IMAGE = getattr(
    settings,
    'ALDRYN_PEOPLE_SHOW_SECONDARY_IMAGE',
    0,
)
ALDRYN_PEOPLE_SHOW_SECONDARY_PHONE = getattr(
    settings,
    'ALDRYN_PEOPLE_SHOW_SECONDARY_PHONE',
    0,
)
