# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import reduce
from django.db.models import Q
from django import forms
from aldryn_categories.models import Category
from js_services.models import Service
import django_filters
from . import models
from .constants import (
    IS_THERE_COMPANIES,
    ADD_FILTERED_CATEGORIES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company


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


class PeopleFilters(django_filters.FilterSet):
    q = SearchInNamesFilter(label='Search the directory')
    category = django_filters.ModelChoiceFilter('categories', label='category', queryset=Category.objects.all())
    service = django_filters.ModelChoiceFilter('services', label='service', queryset=Service.objects.published().all())
    group = django_filters.ModelChoiceFilter('groups', label='group', queryset=models.Group.objects.all())
    letter = django_filters.CharFilter('last_name', 'istartswith')

    class Meta:
        model = models.Person
        fields = ['q', 'category', 'service', 'location', 'group', 'letter']

    def __init__(self, values, *args, **kwargs):
        super(PeopleFilters, self).__init__(values, *args, **kwargs)
        self.filters['category'].extra.update({'empty_label': 'by category'})
        self.filters['service'].extra.update({'empty_label': 'by service'})
        self.filters['location'].extra.update({'empty_label': 'by location'})
        self.filters['group'].extra.update({'empty_label': 'by role'})
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='company', queryset=Company.objects.all())
            self.filters['company'].extra.update({'empty_label': 'by company'})
        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children() if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': 'by %s' % category[1]})
