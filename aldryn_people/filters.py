# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import reduce
from django.db.models import Q
from django import forms
from aldryn_categories.models import Category
from js_services.models import Service
import django_filters
from . import models

class SearchInNamesFilter(django_filters.Filter):

    def filter(self, qs, value):
        value = value or ()
        if len(value) > 0:
            names = value.strip().split()
            if names:
                if len(names) == 2:  # Assuming a first and last name entered
                    qs = qs.filter(
                        translations__first_name__icontains=names[0],
                        translations__last_name__icontains=names[1]
                    )
                else:
                    qu = [
                        Q(translations__first_name__icontains=word) |
                        Q(translations__last_name__icontains=word)
                        for word in names
                    ]
                    qs = qs.filter(
                        reduce(lambda x, y: x | y, qu))
        return qs


class PeopleFilters(django_filters.FilterSet):
    q = SearchInNamesFilter(label='Search the directory')
    categories = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    services = django_filters.ModelChoiceFilter(queryset=Service.objects.all())
    letter = django_filters.CharFilter('translations__last_name', 'istartswith')

    class Meta:
        model = models.Person
        fields = ['q', 'categories', 'services', 'location', 'letter']

    def __init__(self, values, *args, **kwargs):
        super(PeopleFilters, self).__init__(values, *args, **kwargs)
        self.filters['categories'].extra.update({'empty_label': 'by category'})
        self.filters['services'].extra.update({'empty_label': 'by service'})
        self.filters['location'].extra.update({'empty_label': 'by location'})
