# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_translation_tools.sitemaps import I18NSitemap

from .models import Person, Group
from .constants import SITEMAP_CHANGEFREQ, SITEMAP_PRIORITY, TRANSLATE_IS_PUBLISHED
from . import DEFAULT_APP_NAMESPACE


class PeopleSitemap(I18NSitemap):

    changefreq = SITEMAP_CHANGEFREQ
    priority = SITEMAP_PRIORITY

    def __init__(self, *args, **kwargs):
        self.namespace = kwargs.pop('namespace', None)
        if self.namespace == DEFAULT_APP_NAMESPACE:
            self.namespace = None
        self.sitemap_type = kwargs.pop('type', 'xml')
        super(PeopleSitemap, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Person.objects.published()

    def items(self):
        qs = self.get_queryset()
        if self.language is not None:
            qs = qs.language(self.language)
        if self.namespace is not None:
            qs = qs.filter(groups__namespace=self.namespace)
        if self.sitemap_type == 'html':
            qs = qs.exclude(show_on_sitemap=False)
        elif self.sitemap_type == 'xml':
            qs = qs.exclude(show_on_xml_sitemap=False)
        return qs

    def lastmod(self, obj):
        modification_dates = map(lambda plugin: plugin.changed_date, obj.content.get_plugins())
        return max(modification_dates, default=None)

try:
    from js_sitemap.alt_sitemap import SitemapAlt
    class PeopleSitemapAlt(SitemapAlt, PeopleSitemap):
        def get_queryset(self):
            if TRANSLATE_IS_PUBLISHED:
                return Person.objects.published_one_of_trans().prefetch_related('translations').distinct()
            return super(PeopleSitemapAlt, self).get_queryset()

        def languages(self, obj):
            if TRANSLATE_IS_PUBLISHED:
                return obj.translations.filter(is_published_trans=True).values_list('language_code', flat=True)
            return super(PeopleSitemapAlt, self).languages(obj)
except:
    pass
