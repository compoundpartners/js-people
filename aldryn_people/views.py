# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_people.utils import get_valid_languages

from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.translation import get_language_from_request

from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin
from django_filters.views import FilterMixin

from . import DEFAULT_APP_NAMESPACE
from .models import Group, Person
from .filters import PeopleFilters
from .constants import (
    INDEX_GROUP_LIST,
    INDEX_DEFAULT_FILTERS,
    DEFAULT_SORTING,
    SHOW_GROUP_LIST_VIEW_ON_INITIAL_SEARCH,
)


def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang

class EditModeMixin(object):
    """
    A mixin which sets the property 'edit_mode' with the truth value for
    whether a user is logged-into the CMS and is in edit-mode.
    """
    edit_mode = False

    def dispatch(self, request, *args, **kwargs):
        self.edit_mode = (
            self.request.toolbar and self.request.toolbar.edit_mode)
        return super(EditModeMixin, self).dispatch(request, *args, **kwargs)

class FilterFormMixin(object):

    def get_context_data(self, **kwargs):
        data = super(FilterFormMixin, self).get_context_data(**kwargs)
        qs = data['object_list'] if 'object_list' in data else Person.objects.none()
        data['filter'] = PeopleFilters(
            self.request.GET, queryset=qs)
        return data


class LanguageChangerMixin(object):
    """
    Convenience mixin that adds CMS Language Changer support.
    """
    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        set_language_changer(request, self.object.get_absolute_url)
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


class PersonDetailView(PublishedMixin, LanguageChangerMixin, AllowPKsTooMixin,
                       TranslatableSlugMixin, DetailView):
    model = Person
    # context_object_name = 'person'  # The default


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

    def dispatch(self, request, *args, **kwargs):
        if SHOW_GROUP_LIST_VIEW_ON_INITIAL_SEARCH and not request.GET:
            return GroupListView.as_view()(request, *args, **kwargs)
        self.request_language = get_language(request)
        self.request = request
        self.site_id = getattr(get_current_site(self.request), 'id', None)
        self.valid_languages = get_valid_languages(
            DEFAULT_APP_NAMESPACE, self.request_language, self.site_id)
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        # prepare language properties for filtering
        if not self.request.GET and INDEX_DEFAULT_FILTERS:
            qs = qs.filter(**INDEX_DEFAULT_FILTERS)
        if DEFAULT_SORTING:
            qs = qs.order_by(*DEFAULT_SORTING)
        return qs.translated(*self.valid_languages)

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
        return context


class IndexView(FilterFormMixin, TemplateView):
    template_name = 'aldryn_people/index.html'
