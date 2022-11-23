# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cms.admin.placeholderadmin import PlaceholderAdminMixin
from parler.models import TranslationDoesNotExist
from parler.admin import TranslatableAdmin
from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_translation_tools.admin import AllTranslationsMixin
try:
    from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
except:
    from django.contrib.admin.widgets import FilteredSelectMultiple as SortedFilteredSelectMultiple
from cms.utils.i18n import get_current_language, get_language_list
from cms.utils import copy_plugins, get_current_site
from django.db import transaction
from django.db.models import Count
from django.db.models.query import EmptyQuerySet
from django import forms
from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from django.forms import widgets
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import mark_safe
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from .models import Person, Group
from .forms import PersonAdminForm, GroupAdminForm

from .constants import (
    ALDRYN_PEOPLE_HIDE_EMAIL,
    ALDRYN_PEOPLE_HIDE_PHONE,
    ALDRYN_PEOPLE_HIDE_MOBILE,
    ALDRYN_PEOPLE_HIDE_VCARD,
    ALDRYN_PEOPLE_USER_THRESHOLD,
    ALDRYN_PEOPLE_HIDE_SUFFIX,
    ALDRYN_PEOPLE_HIDE_FAX,
    ALDRYN_PEOPLE_HIDE_WEBSITE,
    ALDRYN_PEOPLE_HIDE_FACEBOOK,
    ALDRYN_PEOPLE_HIDE_TWITTER,
    ALDRYN_PEOPLE_HIDE_LINKEDIN,
    ALDRYN_PEOPLE_HIDE_XING,
    ALDRYN_PEOPLE_HIDE_GROUPS,
    ALDRYN_PEOPLE_HIDE_CATEGORIES,
    ALDRYN_PEOPLE_HIDE_LOCATION,
    ALDRYN_PEOPLE_HIDE_USER,
    ALDRYN_PEOPLE_SHOW_SECONDARY_IMAGE,
    ALDRYN_PEOPLE_SHOW_SECONDARY_PHONE,
    ALDRYN_PEOPLE_SUMMARY_RICHTEXT,
    TRANSLATE_IS_PUBLISHED,
    TRANSLATE_VISUAL,
    IS_THERE_COMPANIES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

require_POST = method_decorator(require_POST)


def make_published(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_published_trans = True
            i.save()
    else:
        queryset.update(is_published=True)
make_published.short_description = _(
    "Mark selected as published")

def make_unpublished(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_published_trans = False
            i.save()
    else:
        queryset.update(is_published=False)
make_unpublished.short_description = _(
    "Mark selected as not published")

def make_details_enabled(modeladmin, request, queryset):
    queryset.update(details_enabled=True)
make_details_enabled.short_description = _(
    "Mark selected as details enabled")

def make_not_details_enabled(modeladmin, request, queryset):
    queryset.update(details_enabled=False)
make_not_details_enabled.short_description = _(
    "Mark selected as not details enabled")


class PersonAdmin(PlaceholderAdminMixin,
                  AllTranslationsMixin,
                  TranslatableAdmin):

    actions = (
        make_details_enabled, make_not_details_enabled,
        make_published, make_unpublished,
    )

    form = PersonAdminForm
    list_display = [
        '__str__', 'is_published', ]
    if ALDRYN_PEOPLE_HIDE_GROUPS == 0:
        list_display += ['num_groups',]
        list_filter = ['details_enabled', 'services', 'groups']
    else:
        list_filter = ['details_enabled', 'services']

    search_fields = ('first_name', 'last_name', 'email', 'translations__function')

    filter_horizontal = [
        'categories',
    ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Determines if the User widget should be a drop-down or a raw ID field.
        """
        if ALDRYN_PEOPLE_HIDE_USER == 0:
            # This is a hack to use until get_raw_id_fields() lands in Django:
            # https://code.djangoproject.com/ticket/17881.
            if db_field.name in ['user', ]:
                model = Person._meta.get_field('user').model
                if model.objects.count() > ALDRYN_PEOPLE_USER_THRESHOLD:
                    kwargs['widget'] = admin.widgets.ForeignKeyRawIdWidget(
                        db_field.remote_field, self.admin_site, using=kwargs.get('using'))
                    return db_field.formfield(**kwargs)
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in ['services']:
            kwargs['widget'] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    contact_fields = (
        'visual',
    )
    if ALDRYN_PEOPLE_SHOW_SECONDARY_IMAGE != 0:
        contact_fields += (
            'second_visual',
        )
    if ALDRYN_PEOPLE_HIDE_EMAIL == 0:
        contact_fields += (
            'email',
        )
    if ALDRYN_PEOPLE_HIDE_MOBILE == 0:
        contact_fields += (
            'mobile',
        )
    if ALDRYN_PEOPLE_HIDE_PHONE == 0:
        contact_fields += (
            'phone',
        )
    if ALDRYN_PEOPLE_SHOW_SECONDARY_PHONE != 0:
        contact_fields += (
            'second_phone',
        )
    if ALDRYN_PEOPLE_HIDE_FAX == 0:
        contact_fields += (
            'fax',
        )
    if ALDRYN_PEOPLE_HIDE_WEBSITE == 0:
        contact_fields += (
            'website',
        )
    if ALDRYN_PEOPLE_HIDE_FACEBOOK == 0:
        contact_fields += (
            'facebook',
        )
    if ALDRYN_PEOPLE_HIDE_TWITTER == 0:
        contact_fields += (
            'twitter',
        )
    if ALDRYN_PEOPLE_HIDE_LINKEDIN == 0:
        contact_fields += (
            'linkedin',
        )
    if ALDRYN_PEOPLE_HIDE_XING == 0:
        contact_fields += (
            'xing',
        )
    if ALDRYN_PEOPLE_HIDE_LOCATION == 0:
        contact_fields += (
            'location',
        )
    if ALDRYN_PEOPLE_HIDE_VCARD == 0:
        contact_fields += (
            'vcard_enabled',
        )
    if ALDRYN_PEOPLE_HIDE_USER == 0:
        contact_fields += (
            'user',
        )

    main_fields = (
        'first_name',
        'last_name',
    )
    if ALDRYN_PEOPLE_HIDE_SUFFIX == 0:
        main_fields += (
            'suffix',
        )
    main_fields += (
        'slug',
        'function', 'description',
        'is_published', 'details_enabled',
        'layout_trans',
        'custom_fields',
    )
    advanced_fields = ()
    if ALDRYN_PEOPLE_HIDE_GROUPS == 0:
        advanced_fields += (
            'groups',
        )
    if ALDRYN_PEOPLE_HIDE_CATEGORIES == 0:
        advanced_fields += (
            'categories',
        )
    advanced_fields += (
        'services',
    )
    if IS_THERE_COMPANIES:
        advanced_fields += (
            'companies',
        )
    advanced_fields += (
        'show_on_sitemap',
        'show_on_xml_sitemap',
        'noindex',
        'nofollow',
        'canonical_url',
    )

    fieldsets = (
        (None, {
            'fields': main_fields,
        }),
        (_('Contact (untranslated)'), {
            'fields': contact_fields,
        }),
        (None, {
            'fields': advanced_fields,
        }),
    )


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(group_count=Count('groups'))
        return qs

    def num_groups(self, obj):
        return obj.group_count
    num_groups.short_description = _('# Groups')
    num_groups.admin_order_field = 'group_count'

    def is_published_trans_safe(self, obj):
        return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.safe_translation_getter('is_published_trans', default=False) else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    is_published_trans_safe.short_description = _('Show')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if IS_THERE_COMPANIES:
            obj.companies.clear()
            i = 0
            for company in form.cleaned_data.get('companies'):
                through = obj.companies.through(company=company, person=obj, sort_value=i)
                through.save()
                i += 1

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        for fieldset in fieldsets:
            if len(fieldset) == 2 and 'fields' in fieldset[1]:
                fields = []
                for field in fieldset[1]['fields']:
                    if field  == 'is_published' and TRANSLATE_IS_PUBLISHED:
                        field += '_trans'
                    elif field  in ['visual', 'second_visual'] and TRANSLATE_VISUAL:
                        field += '_trans'
                    fields.append(field)
                fieldset[1]['fields'] = fields
        return fieldsets

    def get_list_display(self, request):
        fields = []
        list_display = super().get_list_display(request)
        for field in list_display:
            if field  == 'is_published' and TRANSLATE_IS_PUBLISHED:
                field += '_trans_safe'
            fields.append(field)
        return fields

    def get_site(self, request):
        site_id = request.session.get('cms_admin_site')
        if not site_id:
            return get_current_site()
        try:
            site = Site.objects._get_site_by_id(site_id)
        except Site.DoesNotExist:
            site = get_current_site()
        return site

    def all_translations(self, object):
        return mark_safe(super().all_translations(object))

    @require_POST
    @transaction.atomic
    def copy_language(self, request, obj_id):
        obj = self.get_object(request, object_id=obj_id)
        source_language = request.POST.get('source_language')
        target_language = request.POST.get('target_language')

        if not self.has_change_permission(request, obj=obj):
            raise PermissionDenied

        if obj is None:
            raise Http404

        if not target_language or not target_language in get_language_list(site_id=self.get_site(request).pk):
            return HttpResponseBadRequest(force_text(_("Language must be set to a supported language!")))

        for placeholder in obj.get_placeholders():
            plugins = list(
                placeholder.get_plugins(language=source_language).order_by('path'))
            if not placeholder.has_add_plugins_permission(request.user, plugins):
                return HttpResponseForbidden(force_text(_('You do not have permission to copy these plugins.')))
            copy_plugins.copy_plugins_to(plugins, placeholder, target_language)
        return HttpResponse("ok")

    def get_urls(self):
        urlpatterns = super().get_urls()
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        return [url(
            r'^(.+)/copy_language/$',
            self.admin_site.admin_view(self.copy_language),
            name='{0}_{1}_copy_language'.format(*info)
        )] + urlpatterns


class GroupAdmin(PlaceholderAdminMixin,
                 AllTranslationsMixin,
                 TranslatableAdmin):

    form = GroupAdminForm
    list_display = ['__str__', 'city', 'num_people', ]
    search_filter = ['translations__name']
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'description',
                'sorting',
                'custom_fields_settings',
                'custom_fields',
            ),
        }),
        (_('Contact (untranslated)'), {
            'fields': (
                'phone',
                'fax',
                'email',
                'website',
                'address',
                'postal_code',
                'city'
            )
        }),
    )

    def get_queryset(self, request):
        qs = super(GroupAdmin, self).get_queryset(request)
        qs = qs.annotate(people_count=Count('people'))
        return qs

    def num_people(self, obj):
        return obj.people_count
    num_people.short_description = _('# People')
    num_people.admin_order_field = 'people_count'

    def all_translations(self, object):
        return mark_safe(super().all_translations(object))


admin.site.register(Person, PersonAdmin)

if ALDRYN_PEOPLE_HIDE_GROUPS == 0:
    admin.site.register(Group, GroupAdmin)
