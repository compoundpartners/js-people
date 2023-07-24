# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_people.utils import get_valid_languages

from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.translation import get_language_from_request
from django.utils.cache import patch_cache_control
from django.utils.timezone import now

from cms.cache.page import set_page_cache, get_page_cache
from cms.utils.compat import DJANGO_2_2, DJANGO_3_0
from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin
from django_filters.views import FilterMixin
from aldryn_apphooks_config.utils import get_app_instance
from js_locations.models import Location

from . import DEFAULT_APP_NAMESPACE
from .models import Group, Person
from .filters import PeopleFilters
from .constants import (
    INDEX_GROUP_LIST,
    INDEX_DEFAULT_FILTERS,
    DEFAULT_SORTING,
    SHOW_INDEX_VIEW_ON_INITIAL_SEARCH,
    SHOW_GROUP_LIST_VIEW_ON_INITIAL_SEARCH,
    IS_THERE_COMPANIES,
    USE_CACHE,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang

class CachedMixin():
    def use_cache(self, request):
        is_authenticated = request.user.is_authenticated
        model_name = str(self.model.__name__ if self.model else self.queryset.model.__name__)
        return request.method.lower() == 'get' and model_name in USE_CACHE and USE_CACHE[model_name] and (
            not hasattr(request, 'toolbar') or (
                not request.toolbar.edit_mode_active and not request.toolbar.show_toolbar and not is_authenticated
            )
        )

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        response_timestamp = now()
        if self.use_cache(request):
            cache_content = get_page_cache(request)
            if cache_content is not None:
                content, headers, expires_datetime = cache_content
                response = HttpResponse(content)
                response.xframe_options_exempt = True
                if DJANGO_2_2 or DJANGO_3_0:
                    response._headers = headers
                else:
                    #  for django3.2 and above. response.headers replaces response._headers in earlier versions of django
                    response.headers = headers
                # Recalculate the max-age header for this cached response
                max_age = int(
                    (expires_datetime - response_timestamp).total_seconds() + 0.5)
                patch_cache_control(response, max_age=max_age)
                return response
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.use_cache(self.request):
            response.add_post_render_callback(set_page_cache)
        return response


class EditModeMixin(object):
    """
    A mixin which sets the property 'edit_mode' with the truth value for
    whether a user is logged-into the CMS and is in edit-mode.
    """
    edit_mode = False

    def dispatch(self, request, *args, **kwargs):
        self.edit_mode = (
            self.request.toolbar and self.request.toolbar.edit_mode_active)
        return super(EditModeMixin, self).dispatch(request, *args, **kwargs)

class FilterFormMixin(object):

    def get_context_data(self, **kwargs):
        data = super(FilterFormMixin, self).get_context_data(**kwargs)
        data['filter'] = PeopleFilters(
            self.request.GET, queryset=Person.objects.none())
        return data


class LanguageChangerMixin(object):
    """
    Convenience mixin that adds CMS Language Changer support.
    """
    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        set_language_changer(request, self.object.get_public_url)
        return super(LanguageChangerMixin, self).get(request, *args, **kwargs)


class PublishedMixin(EditModeMixin):
    def get_queryset(self):
        qs = super(PublishedMixin, self).get_queryset()
        user = self.request.user
        user_can_edit = user.is_staff or user.is_superuser
        if not (self.edit_mode or user_can_edit):
            qs = qs.published()
        return qs


class AllowPKsTooMixin(object):
    def get_object(self, queryset=None):
        """
        Bypass TranslatableSlugMixin if we are using PKs. You would only use
        this if you have a view that supports accessing the object by pk or
        by its translatable slug.

        NOTE: This should only be used on DetailViews and this mixin MUST be
        placed to the left of TranslatableSlugMixin. In fact, for best results,
        declare your view like this:

            MyView(…, AllowPKsTooMixin, TranslatableSlugMixin, DetailView):
        """
        if self.pk_url_kwarg in self.kwargs:
            return super(DetailView, self).get_object(queryset)

        # OK, just let Parler have its way with it.
        return super(AllowPKsTooMixin, self).get_object(queryset)


class DownloadVcardView(PublishedMixin, AllowPKsTooMixin, TranslatableSlugMixin, DetailView):
    model = Person

    def get(self, request, *args, **kwargs):
        person = self.get_object()
        if not person.vcard_enabled:
            raise Http404

        filename = "%s.vcf" % str(person)
        vcard = person.get_vcard(request)
        try:
            vcard = vcard.decode('utf-8').encode('ISO-8859-1')
        except UnicodeError:
            pass
        response = HttpResponse(vcard, content_type="text/x-vCard")
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            filename)
        return response


class PersonDetailView(CachedMixin, PublishedMixin, LanguageChangerMixin, AllowPKsTooMixin,
                       TranslatableSlugMixin, DetailView):
    model = Person
    # context_object_name = 'person'  # The default

    @property
    def template_name_suffix(self):
        return '_%s' %  (self.object.layout_trans or 'detail')


class GroupDetailView(LanguageChangerMixin, AllowPKsTooMixin,
                      TranslatableSlugMixin, DetailView):
    model = Group


class GroupListView(FilterFormMixin, ListView):
    model = Group

    def dispatch(self, request, *args, **kwargs):
        self.request_language = get_language(request)
        self.request = request
        self.site_id = getattr(get_current_site(self.request), 'id', None)
        self.valid_languages = get_valid_languages(
            DEFAULT_APP_NAMESPACE, self.request_language, self.site_id)
        return super(GroupListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(GroupListView, self).get_queryset().order_by('sorting')
        if INDEX_GROUP_LIST:
            qs = qs.filter(translations__slug__in=INDEX_GROUP_LIST)
        # prepare language properties for filtering
        return qs.translated(*self.valid_languages)

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        if not INDEX_GROUP_LIST:
            qs_ungrouped = Person.objects.published().filter(groups__isnull=True)
            context['ungrouped_people'] = qs_ungrouped.translated(
                *self.valid_languages)
        return context


class SearchView(FilterMixin, PublishedMixin, ListView):
    model = Person
    template_name = 'aldryn_people/search.html'
    paginate_by = 20
    namespace = DEFAULT_APP_NAMESPACE
    config = None
    config_type = None

    def get_strict(self):
        return False

    def dispatch(self, request, *args, **kwargs):
        self.namespace, self.config = get_app_instance(request)
        request.current_app = self.namespace
        if (not request.GET or any(map(lambda x: x in request.GET, ['edit_off', 'edit', 'structure']))) and self.namespace == DEFAULT_APP_NAMESPACE:
            if SHOW_INDEX_VIEW_ON_INITIAL_SEARCH:
                return IndexView.as_view()(request, *args, **kwargs)
            elif SHOW_GROUP_LIST_VIEW_ON_INITIAL_SEARCH:
                return GroupListView.as_view()(request, *args, **kwargs)
        self.request_language = get_language(request)
        self.request = request
        self.site_id = getattr(get_current_site(self.request), 'id', None)
        self.valid_languages = get_valid_languages(
            self.namespace, self.request_language, self.site_id)
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        # prepare language properties for filtering
        if self.config:
            if isinstance(self.config, Group) and self.namespace != DEFAULT_APP_NAMESPACE:
                qs = qs.filter(groups=self.config)
                self.config_type = 'Group'
            elif isinstance(self.config, Location):
                qs = qs.filter(location=self.config)
                self.config_type = 'Location'
            elif IS_THERE_COMPANIES and isinstance(self.config, Company):
                self.config_type = 'Company'
                qs = qs.filter(companies=self.config)
        elif not self.request.GET and INDEX_DEFAULT_FILTERS:
            qs = qs.filter(**INDEX_DEFAULT_FILTERS)
        if DEFAULT_SORTING:
            qs = qs.order_by(*DEFAULT_SORTING)
        return qs

    def get(self, request, *args, **kwargs):
        self.filterset = PeopleFilters(self.request.GET, queryset=self.get_queryset())

        if not self.filterset.is_bound or self.filterset.is_valid() or not self.get_strict():
            self.object_list = self.filterset.qs.distinct()
        else:
            self.object_list = self.filterset.queryset.none()

        context = self.get_context_data(filter=self.filterset,
                                        object_list=self.object_list)
        return self.render_to_response(context)

    def get_pagination_options(self):
        options = {
            'pages_start': 10,
            'pages_visible': 2,
        }
        pages_visible_negative = -options['pages_visible']
        options['pages_visible_negative'] = pages_visible_negative
        options['pages_visible_total'] = options['pages_visible'] + 1
        options['pages_visible_total_negative'] = pages_visible_negative - 1
        return options

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['pagination'] = self.get_pagination_options()
        context['config'] = self.config
        context['config_type'] = self.config_type
        return context

    def render_to_response(self, context, **response_kwargs):
        if 'current_app' in response_kwargs:  # pragma: no cover
            response_kwargs['current_app'] = self.namespace
        return super(SearchView, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        if self.namespace != DEFAULT_APP_NAMESPACE:
            return 'aldryn_people/list.html'
        return super(SearchView, self).get_template_names()


class IndexView(FilterFormMixin, TemplateView):
    template_name = 'aldryn_people/index.html'
