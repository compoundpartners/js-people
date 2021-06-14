# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import reduce
from django.db.models import Q
from django import forms
from aldryn_categories.models import Category
from js_services.models import Service
from js_locations.models import Location
import django_filters
from . import models
from .constants import (
    UPDATE_SEARCH_DATA_ON_SAVE,
    IS_THERE_COMPANIES,
    ADD_FILTERED_CATEGORIES,
    ADDITIONAL_EXCLUDE,
    FILTER_EMPTY_LABELS,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

try:
    from custom.aldryn_people.filters import CustomFilterMixin
except:
    class CustomFilterMixin(object):
        pass


class SearchInNamesFilter(django_filters.Filter):

    def filter(self, qs, value):
        value = value or ()
        if len(value) > 0:
            names = value.strip().split()
            if names:
                if len(names) == 2:  # Assuming a first and last name entered
                    qs = qs.filter(
                        first_name__icontains=names[0],
                        last_name__icontains=names[1]
                    )
                else:
                    qu = [
                        Q(first_name__icontains=word) |
                        Q(last_name__icontains=word)
                        for word in names
                    ]
                    qs = qs.filter(
                        reduce(lambda x, y: x | y, qu))
        return qs

class SearchFilter(django_filters.Filter):
    def filter(self, qs, values):
        values = values or ''
        if len(values) > 0:
            for value in values.strip().split():
                value = value.strip()
                if value:
                    qs = qs.filter(translations__search_data__icontains=value)
        return qs


class PeopleFilters(CustomFilterMixin, django_filters.FilterSet):
    name = SearchInNamesFilter(label='Search the directory')
    q = SearchInNamesFilter(label='Search the directory')
    category = django_filters.ModelChoiceFilter('categories', label='category', empty_label='by category', queryset=Category.objects.exclude(**ADDITIONAL_EXCLUDE.get('category', {})))
    service = django_filters.ModelChoiceFilter('services', label='service', empty_label='by service', queryset=Service.objects.published().exclude(**ADDITIONAL_EXCLUDE.get('service', {})))
    group = django_filters.ModelChoiceFilter('groups', label='group', empty_label='by role', queryset=models.Group.objects.exclude(**ADDITIONAL_EXCLUDE.get('group', {})))
    letter = django_filters.CharFilter('last_name', 'istartswith')
    location = django_filters.ModelChoiceFilter('location', label='location', empty_label='by location', queryset=Location.objects.published().exclude(**ADDITIONAL_EXCLUDE.get('location', {})))

    class Meta:
        model = models.Person
        fields = ['q', 'name', 'category', 'service', 'location', 'group', 'letter']

    def __init__(self, values, *args, **kwargs):
        super(PeopleFilters, self).__init__(values, *args, **kwargs)
        if UPDATE_SEARCH_DATA_ON_SAVE:
            self.filters['q'] = SearchFilter(label='Search the directory')
        selects = ['location', 'category', 'service', 'group']
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='company', empty_label='by company', queryset=Company.objects.exclude(**ADDITIONAL_EXCLUDE.get('company', {})))
            selects.append('company')

        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children().exclude(**ADDITIONAL_EXCLUDE.get(category[0], {})) if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': 'by %s' % category[1]})
                selects.append(name)

        self.set_empty_labels(**FILTER_EMPTY_LABELS)

        for select in selects[:]:
            self.filters['%s_filtered' % select] = django_filters.ModelChoiceFilter(self.filters[select].field_name)
            self.filters['%s_filtered' % select].label = self.filters[select].label
            self.filters['%s_filtered' % select].extra['empty_label'] = self.filters[select].extra['empty_label']
            self.filters['%s_filtered' % select].queryset = self.filters[select].queryset.filter(**{'%s__in' % ('people' if select in ['group', 'company'] else 'person') :self.queryset}).distinct()
            selects.append('%s_filtered' % select)

        for field in selects:
            self.sort_choices(self.filters[field])

    def set_empty_labels(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.filters:
                self.filters[key].extra['empty_label'] = value

    def sort_choices(self, field):
        field = field.field
        if isinstance(field.choices, django_filters.fields.ModelChoiceIterator):
            choices = [(obj.pk, str(obj)) for obj in field.choices.queryset]
            field.iterator = django_filters.fields.ChoiceIterator
            field._set_choices(sorted(choices, key=lambda item: item[1]))
