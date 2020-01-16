# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import six
from aldryn_people.vcard import Vcard

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
import warnings

try:
    from django.utils.encoding import force_unicode
except ImportError:
    try:
        from django.utils.encoding import force_text as force_unicode
    except ImportError:
        def force_unicode(value):
            return value.decode()

from django.conf import settings
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:
    # Django 2.0
    from django.urls import reverse, NoReverseMatch
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.dispatch import receiver
from django.db.models.signals import post_save

from django.utils.translation import ugettext_lazy as _, override
try:
    from django.utils.translation import force_text
except ImportError:
    # Django 2.0
    def force_text(value):
        return value.decode()
from six import text_type

from sortedm2m.fields import SortedManyToManyField
from aldryn_translation_tools.models import (
    TranslatedAutoSlugifyMixin,
    TranslationHelperMixin,
)
from aldryn_newsblog.utils import get_plugin_index_data, get_request, strip_tags
from aldryn_categories.fields import CategoryManyToManyField
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, get_default_language
from djangocms_text_ckeditor.fields import HTMLField
from djangocms_icon.fields import Icon
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields

from .managers import PeopleManager
from .utils import get_additional_styles
from . import DEFAULT_APP_NAMESPACE

from .constants import (
    UPDATE_SEARCH_DATA_ON_SAVE,
    IS_THERE_COMPANIES,
)

@python_2_unicode_compatible
class Group(TranslationHelperMixin, TranslatedAutoSlugifyMixin,
            TranslatableModel):
    slug_source_field_name = 'name'
    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255,
                              help_text=_("Provide this group's name.")),
        description=HTMLField(_('description'), blank=True),
        slug=models.SlugField(
            _('slug'), max_length=255, default='',
            blank=True,
            help_text=_("Leave blank to auto-generate a unique slug.")),
    )
    address = models.TextField(
        verbose_name=_('address'), blank=True)
    postal_code = models.CharField(
        verbose_name=_('postal code'), max_length=20, blank=True)
    city = models.CharField(
        verbose_name=_('city'), max_length=255, blank=True)
    phone = models.CharField(
        verbose_name=_('phone'), null=True, blank=True, max_length=100)
    fax = models.CharField(
        verbose_name=_('fax'), null=True, blank=True, max_length=100)
    email = models.EmailField(
        verbose_name=_('email'), blank=True, default='')
    website = models.URLField(
        verbose_name=_('website'), null=True, blank=True)
    sorting = models.PositiveSmallIntegerField(
        verbose_name=_('sorting field'), default=1,
        help_text=_('first with low value'))


    @property
    def company_name(self):
        warnings.warn(
            '"Group.company_name" has been refactored to "Group.name"',
            DeprecationWarning
        )
        return self.safe_translation_getter('name')

    @property
    def company_description(self):
        warnings.warn(
            '"Group.company_description" has been refactored to '
            '"Group.description"',
            DeprecationWarning
        )
        return self.safe_translation_getter('description')

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def __str__(self):
        return self.safe_translation_getter(
            'name', default=_('Group: {0}').format(self.pk))

    def get_absolute_url(self, language=None):
        if not language:
            language = get_current_language() or get_default_language()
        slug, language = self.known_translation_getter(
            'slug', None, language_code=language)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            return reverse('%s:group-detail' % DEFAULT_APP_NAMESPACE, kwargs=kwargs)


@python_2_unicode_compatible
class Person(TranslationHelperMixin, TranslatedAutoSlugifyMixin,
             TranslatableModel):
    update_search_on_save = UPDATE_SEARCH_DATA_ON_SAVE

    translations = TranslatedFields(
        first_name_trans=models.CharField(
            _('first name'), max_length=255, blank=False,
            default='', help_text=_("Provide this person's first name.")),
        last_name_trans=models.CharField(
            _('last name'), max_length=255, blank=False,
            default='', help_text=_("Provide this person's last name.")),
        suffix=models.CharField(
            _('suffix'), max_length=60, blank=True,
            default='', help_text=_("Provide this person's suffix.")),
        slug=models.SlugField(
            _('unique slug'), max_length=255, blank=True,
            default='',
            help_text=_("Leave blank to auto-generate a unique slug.")),
        function=models.CharField(_('role'), max_length=255, blank=True, default=''),
        description=HTMLField(_('description'), blank=True, default=''),
        search_data=models.TextField(blank=True, editable=False)
    )
    first_name = models.CharField(
        _('first name'), max_length=255, blank=False,
        default='', help_text=_("Provide this person's first name."))
    last_name = models.CharField(
        _('last name'), max_length=255, blank=False,
        default='', help_text=_("Provide this person's last name."))
    phone = models.CharField(
        verbose_name=_('phone'), null=True, blank=True, max_length=100)
    second_phone = models.CharField(
        verbose_name=_('secondary phone'), null=True, blank=True, max_length=100)
    mobile = models.CharField(
        verbose_name=_('mobile'), null=True, blank=True, max_length=100)
    fax = models.CharField(
        verbose_name=_('fax'), null=True, blank=True, max_length=100)
    email = models.EmailField(
        verbose_name=_("email"), blank=True, default='')
    facebook = models.URLField(
        verbose_name=_('facebook'), null=True, blank=True, max_length=200)
    twitter = models.CharField(
        verbose_name=_('twitter'), null=True, blank=True, max_length=100)
    linkedin = models.URLField(
        verbose_name=_('linkedin'), null=True, blank=True, max_length=200)
    location = models.ForeignKey('js_locations.Location',
        on_delete=models.SET_NULL, verbose_name=_('location'), null=True, blank=True)
    website = models.URLField(
        verbose_name=_('website'), null=True, blank=True)
    groups = SortedManyToManyField(
        'aldryn_people.Group', default=None, blank=True, related_name='people',
        help_text=_('Choose and order the groups for this person, the first '
                    'will be the "primary group".'))
    visual = FilerImageField(
        null=True, blank=True, default=None, on_delete=models.SET_NULL)
    second_visual = FilerImageField(
        null=True, blank=True, default=None, on_delete=models.SET_NULL,
        related_name='second_person_visual')
    vcard_enabled = models.BooleanField(
        verbose_name=_('enable vCard download'), default=True)
    is_published = models.BooleanField(
        verbose_name=_('show on website'), default=True)
    user = models.OneToOneField(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True, blank=True, related_name='persons')
    categories = CategoryManyToManyField('aldryn_categories.Category',
         verbose_name=_('categories'), blank=True)
    services = SortedManyToManyField('js_services.Service',
         verbose_name=_('services'), blank=True)
    content = PlaceholderField('content',
        related_name='person_content')
    placeholder_sidebar = PlaceholderField('sidebar')

    show_on_sitemap = models.BooleanField(_('Show on sitemap'), null=False, default=True)
    show_on_xml_sitemap = models.BooleanField(_('Show on xml sitemap'), null=False, default=True)
    noindex = models.BooleanField(_('noindex'), null=False, default=False)
    nofollow = models.BooleanField(_('nofollow'), null=False, default=False)

    objects = PeopleManager()

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')

    def __str__(self):
        pkstr = str(self.pk)

        if six.PY2:
            pkstr = six.u(pkstr)
        # name = ' '.join((
        #     self.safe_translation_getter(
        #         'first_name',
        #         default='',
        #         any_language=True
        #     ),
        #     self.safe_translation_getter(
        #         'last_name',
        #         default='',
        #         any_language=True
        #     )
        # )).strip()
        # name = 'TESTING'  #DEBUG
        name = ' '.join((self.first_name, self.last_name)).strip()
        return name if len(name) > 0 else pkstr

    @property
    def primary_group(self):
        """Simply returns the first in `groups`, if any, else None."""
        return self.groups.first()

    @property
    def primary_company(self):
        if IS_THERE_COMPANIES:
            return self.companies.first()

    @property
    def comment(self):
        return self.safe_translation_getter('description', '')

    @property
    def sorted_companies(self):
        if IS_THERE_COMPANIES:
            return [obj.company for obj in self.companies.through.objects.filter(person=self).order_by('sort_value')]
        else:
            []

    def get_search_data(self, language=None, request=None):
        """
        Provides an index for use with Haystack, or, for populating
        Event.translations.search_data.
        """
        if not self.pk:
            return ''
        if language is None:
            language = get_current_language()
        if request is None:
            request = get_request(language=language)
        text_bits = [self.first_name]
        text_bits.append(self.last_name)
        text_bits.append(self.safe_translation_getter('function', ''))
        description = self.safe_translation_getter('description', '')
        text_bits.append(strip_tags(description))
        for category in self.categories.all():
            text_bits.append(
                force_unicode(category.safe_translation_getter('name')))
        for service in self.services.all():
            text_bits.append(
                force_unicode(service.safe_translation_getter('title')))
        if self.content:
            plugins = self.content.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                plugin_text_content = ' '.join(
                    get_plugin_index_data(base_plugin, request))
                text_bits.append(plugin_text_content)
        return ' '.join(text_bits)

    def save(self, *args, **kwargs):
        if self.update_search_on_save:
            self.search_data = self.get_search_data()
        super(Person, self).save(*args, **kwargs)

    def get_absolute_url(self, language=None):
        if not language:
            language = get_current_language()
        slug, language = self.known_translation_getter(
            'slug', None, language_code=language)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            # do not fail with 500 error so that if detail view can't be
            # resolved we still can use plugins.
            try:
                url = reverse('%s:person-detail' % DEFAULT_APP_NAMESPACE, kwargs=kwargs)
            except NoReverseMatch:
                url = ''
        return url

    def get_vcard_url(self, language=None):
        if not language:
            language = get_current_language()
        slug = self.safe_translation_getter(
            'slug', None, language_code=language, any_language=False)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            return reverse('%s:download_vcard' % DEFAULT_APP_NAMESPACE, kwargs=kwargs)

    def get_vcard(self, request=None):
        vcard = Vcard()
        function = self.safe_translation_getter('function')

        safe_name = self.name()
        vcard.add_line('FN', safe_name)
        vcard.add_line('N', [None, safe_name, None, None, None])

        if self.visual:
            ext = self.visual.extension.upper()
            try:
                with open(self.visual.path, 'rb') as f:
                    data = force_text(base64.b64encode(f.read()))
                    vcard.add_line('PHOTO', data, TYPE=ext, ENCODING='b')
            except IOError:
                if request:
                    url = urlparse.urljoin(request.build_absolute_uri(),
                                           self.visual.url),
                    vcard.add_line('PHOTO', url, TYPE=ext)

        if self.email:
            vcard.add_line('EMAIL', self.email)

        if function:
            vcard.add_line('TITLE', self.function)

        if self.phone:
            vcard.add_line('TEL', self.phone, TYPE='WORK')
        if self.mobile:
            vcard.add_line('TEL', self.mobile, TYPE='CELL')

        if self.fax:
            vcard.add_line('TEL', self.fax, TYPE='FAX')
        if self.website:
            vcard.add_line('URL', self.website)

        if self.primary_company:
            vcard.add_line('ORG', self.primary_company.name)

        if self.primary_group:
            group_name = self.primary_group.safe_translation_getter(
                'name', default="Group: {0}".format(self.primary_group.pk))
            if group_name and not self.primary_company:
                vcard.add_line('ORG', group_name)
            if (self.primary_group.address or self.primary_group.city or
                    self.primary_group.postal_code):
                vcard.add_line('ADR', (
                    None, None,
                    self.primary_group.address,
                    self.primary_group.city,
                    None,
                    self.primary_group.postal_code,
                    None,
                ), TYPE='WORK')

            if self.primary_group.phone:
                vcard.add_line('TEL', self.primary_group.phone, TYPE='WORK')
            if self.primary_group.fax:
                vcard.add_line('TEL', self.primary_group.fax, TYPE='FAX')
            if self.primary_group.website:
                vcard.add_line('URL', self.primary_group.website)

        return six.b('{}'.format(vcard))

    def get_slug_source(self):
        return self.__str__()

    def name(self):
        return self.__str__()

    def related_articles(self, article_category=None):
        qs = self.article_set.published() | self.author_2.published() | self.author_3.published()
        if article_category:
            return qs.filter(app_config__namespace=article_category).distinct()
        return qs.distinct()

    def related_events(self, event_category=None):
        if hasattr(self, 'event_set'):
            qs = self.event_set.published() | self.host_2.published() | self.host_3.published()
            if event_category:
                return qs.filter(app_config__namespace=event_category).distinct()
            return qs.distinct().order_by('-event_start')

    def related_upcoming_events(self, event_category=None):
        if hasattr(self, 'event_set'):
            qs = self.event_set.upcoming() | self.host_2.upcoming() | self.host_3.upcoming()
            if event_category:
                return qs.filter(app_config__namespace=event_category).distinct()
            return qs.distinct().order_by('event_start')

    def related_past_events(self, event_category=None):
        if hasattr(self, 'event_set'):
            qs = self.event_set.past() | self.host_2.past() | self.host_3.past()
            if event_category:
                return qs.filter(app_config__namespace=event_category).distinct()
            return qs.distinct().order_by('-event_start')

    def related_services(self, service_category=None):
        if service_category:
            return self.services.published().filter(sections__namespace=service_category)
        return self.services.published().all()

    #def __getattr__(cls, name):
        #if not hasattr(Person, name):
            #if name.startswith('related_articles_'):
                #category = name.split('related_articles_')[1].replace('_', '-')
                #def wrapper(self):
                    #return self.related_articles(category)
                #setattr(Person, name, wrapper)
                #return getattr(cls, name)
            #elif name.startswith('related_services_'):
                #category = name.split('related_services_')[1].replace('_', '-')
                #def wrapper(self):
                    #return self.services(category)
                #setattr(Person, name, wrapper)
                #return getattr(cls, name)
        #raise AttributeError


@python_2_unicode_compatible
class BasePeoplePlugin(CMSPlugin):

    STYLE_CHOICES = [
        ('standard', _('Standard')),
        ('feature', _('Feature'))
    ] + get_additional_styles()

    style = models.CharField(
        _('Style'), choices=STYLE_CHOICES,
        default=STYLE_CHOICES[0][0], max_length=50)

    people = SortedManyToManyField(
        Person, blank=True,
        help_text=_('Select and arrange specific people, or, leave blank to '
                    'select all.')
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
    )

    class Meta:
        abstract = True

    def copy_relations(self, oldinstance):
        self.people = oldinstance.people.all()

    def get_selected_people(self):
        return self.people.published().select_related('visual')

    def __str__(self):
        return text_type(self.pk)


class PeoplePlugin(BasePeoplePlugin):

    group_by_group = models.BooleanField(
        verbose_name=_('group by group'),
        default=True,
        help_text=_('Group people by their group.')
    )
    show_ungrouped = models.BooleanField(
        verbose_name=_('show ungrouped'),
        default=False,
        help_text=_('When using "group by group", show ungrouped people too.')
    )
    show_links = models.BooleanField(
        verbose_name=_('Show links to Detail Page'), default=False)
    show_vcard = models.BooleanField(
        verbose_name=_('Show links to download vCard'), default=False)

    class Meta:
        abstract = False


@python_2_unicode_compatible
class RelatedPeoplePlugin(CMSPlugin):

    # NOTE: This one does NOT subclass NewsBlogCMSPlugin. This is because this
    # plugin can really only be placed on the article detail view in an apphook.
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, on_delete=models.CASCADE, related_name='+', parent_link=True)

    title = models.CharField(max_length=255, blank=True, verbose_name=_('Title'))
    icon = Icon(blank=False, default='')
    image = FilerImageField(on_delete=models.SET_NULL, null=True, blank=True, related_name="main_image")
    number_of_people = models.PositiveSmallIntegerField(verbose_name=_('Number of people'))
    layout = models.CharField(max_length=30, verbose_name=_('layout'))
    related_people = SortedManyToManyField(Person, verbose_name=_('key people'), blank=True, symmetrical=False)
    related_groups = SortedManyToManyField(Group, verbose_name=_('related groups'), blank=True, symmetrical=False)
    related_locations = SortedManyToManyField('js_locations.Location', verbose_name=_('related locations'), blank=True, symmetrical=False)
    related_categories = SortedManyToManyField('aldryn_categories.Category', verbose_name=_('related categories'), blank=True, symmetrical=False)
    related_services = SortedManyToManyField('js_services.Service', verbose_name=_('related services'), blank=True, symmetrical=False)
    more_button_is_shown = models.BooleanField(blank=True, default=False, verbose_name=_('Show “See More Button”'))
    more_button_text = models.CharField(max_length=255, blank=True, verbose_name=_('See More Button Text'))
    more_button_link = models.CharField(max_length=255, blank=True, verbose_name=_('See More Button Link'))

    def copy_relations(self, oldinstance):
        self.related_people = oldinstance.related_people.all()
        self.related_groups = oldinstance.related_groups.all()
        self.related_locations = oldinstance.related_locations.all()
        self.related_services = oldinstance.related_services.all()
        self.related_categories = oldinstance.related_categories.all()
        if IS_THERE_COMPANIES:
            self.related_companies = oldinstance.related_companies.all()

    def __str__(self):
        return text_type(self.pk)


@receiver(post_save, dispatch_uid='person_update_search_data')
def update_search_data(sender, instance, **kwargs):
    is_cms_plugin = issubclass(instance.__class__, CMSPlugin)

    if Person.update_search_on_save and is_cms_plugin:
        placeholder = (getattr(instance, '_placeholder_cache', None) or
                       instance.placeholder)
        if hasattr(placeholder, '_attached_model_cache'):
            if placeholder._attached_model_cache == Person and placeholder.slot == 'content':
                person = placeholder._attached_model_cache.objects.language(
                    instance.language).get(content=placeholder.pk)
                person.search_data = person.get_search_data(instance.language)
                person.save()
