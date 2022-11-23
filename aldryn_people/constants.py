# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.text import slugify

UPDATE_SEARCH_DATA_ON_SAVE = getattr(
    settings,
    'PEOPLE_UPDATE_SEARCH_DATA_ON_SAVE',
    False,
)

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

ALDRYN_PEOPLE_HIDE_EMAIL = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_EMAIL',
    0,
)
ALDRYN_PEOPLE_HIDE_PHONE = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_PHONE',
    0,
)
ALDRYN_PEOPLE_HIDE_MOBILE = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_MOBILE',
    0,
)
ALDRYN_PEOPLE_HIDE_VCARD = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_VCARD',
    0,
)
ALDRYN_PEOPLE_HIDE_SUFFIX = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_SUFFIX',
    0,
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
ALDRYN_PEOPLE_HIDE_XING = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_XING',
    0,
)
ALDRYN_PEOPLE_HIDE_GROUPS = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_GROUPS',
    0,
)
ALDRYN_PEOPLE_HIDE_CATEGORIES = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_CATEGORIES',
    0,
)
ALDRYN_PEOPLE_HIDE_LOCATION = getattr(
    settings,
    'ALDRYN_PEOPLE_HIDE_LOCATION',
    0,
)
ALDRYN_PEOPLE_HIDE_USER = getattr(
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
ALDRYN_PEOPLE_SUMMARY_RICHTEXT = getattr(
    settings,
    'ALDRYN_PEOPLE_SUMMARY_RICHTEXT',
    0,
)
ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'ALDRYN_PEOPLE_ADD_FILTERED_CATEGORIES',
    [],
)
ADDITIONAL_EXCLUDE = getattr(
    settings,
    'ALDRYN_PEOPLE_ADDITIONAL_EXCLUDE',
    {},
)
SHOW_GROUP_LIST_VIEW = getattr(
    settings,
    'ALDRYN_PEOPLE_SHOW_GROUP_LIST_VIEW',
    False,
)
SHOW_GROUP_LIST_VIEW_ON_INITIAL_SEARCH = getattr(
    settings,
    'ALDRYN_PEOPLE_SHOW_GROUP_LIST_VIEW_ON_INITIAL_SEARCH',
    True,
)
SHOW_INDEX_VIEW_ON_INITIAL_SEARCH = getattr(
    settings,
    'ALDRYN_PEOPLE_SHOW_INDEX_VIEW_ON_INITIAL_SEARCH',
    False,
)
URL_PREFIX = getattr(
    settings,
    'ALDRYN_PEOPLE_URL_PREFIX',
    '',
)
INDEX_GROUP_LIST = getattr(
    settings,
    'ALDRYN_PEOPLE_INDEX_GROUP_LIST',
    [],
)
INDEX_DEFAULT_FILTERS = getattr(
    settings,
    'ALDRYN_PEOPLE_INDEX_DEFAULT_FILTERS',
    {},
)
DEFAULT_SORTING = getattr(
    settings,
    'ALDRYN_PEOPLE_DEFAULT_SORTING',
    ('last_name',),
)
SITEMAP_CHANGEFREQ = getattr(
    settings,
    'ALDRYN_PEOPLE_SITEMAP_CHANGEFREQ',
    'monthly',
)
SITEMAP_PRIORITY = getattr(
    settings,
    'ALDRYN_PEOPLE_SITEMAP_PRIORITY',
    0.5,
)
RELATED_PEOPLE_LAYOUT = getattr(
    settings,
    'PEOPLE_RELATED_LAYOUT',
    ()
)
TRANSLATE_IS_PUBLISHED = getattr(
    settings,
    'ALDRYN_PEOPLE_TRANSLATE_IS_PUBLISHED',
    False
)
TRANSLATE_VISUAL = getattr(
    settings,
    'ALDRYN_PEOPLE_TRANSLATE_VISUAL',
    True
)
if len(RELATED_PEOPLE_LAYOUT) == 0 or len(RELATED_PEOPLE_LAYOUT[0]) != 2:
    RELATED_PEOPLE_LAYOUT = zip(list(map(lambda s: slugify(s).replace('-', '_'), ('default',) + RELATED_PEOPLE_LAYOUT)), ('default',) + RELATED_PEOPLE_LAYOUT)

PERSON_CUSTOM_FIELDS = getattr(
    settings,
    'ALDRYN_PEOPLE_PERSON_CUSTOM_FIELDS',
    {},
)
GROUP_CUSTOM_FIELDS = getattr(
    settings,
    'ALDRYN_PEOPLE_GROUP_CUSTOM_FIELDS',
    {},
)

FILTER_EMPTY_LABELS = getattr(
    settings,
    'SEARCH_FILTER_EMPTY_LABELS',
    {}
)
FILTER_EMPTY_LABELS.update(getattr(
    settings,
    'PEOPLE_FILTER_EMPTY_LABELS',
    {}
))

PERSON_LAYOUTS = getattr(
    settings,
    'PEOPLE_PERSON_LAYOUTS',
    (),
)
PERSON_LAYOUT_CHOICES = list(PERSON_LAYOUTS)
if len(PERSON_LAYOUTS) == 0 or len(PERSON_LAYOUTS[0]) != 2:
    PERSON_LAYOUT_CHOICES = zip(list(map(lambda s: slugify(s).replace('-', '_'), ('',) + PERSON_LAYOUTS)), ('default',) + PERSON_LAYOUTS)
else:
    PERSON_LAYOUT_CHOICES.insert(0, ('', 'default'))

try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
