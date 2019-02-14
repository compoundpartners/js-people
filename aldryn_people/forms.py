# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from aldryn_categories.models import Category
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple, SortedMultipleChoiceField
from itertools import chain
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt

from . import models

from .constants import (
    ALDRYN_PEOPLE_HIDE_GROUPS,
    ALDRYN_PEOPLE_HIDE_LOCATION,
)

LAYOUT_CHOICES = [
    ('cols', 'Columns'),
    ('rows', 'Rows'),
    ('hero', 'Hero'),
    ('people', 'People'),
]

STATIC_URL = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)


class RelatedPeoplePluginForm(forms.ModelForm):

    layout = forms.ChoiceField(LAYOUT_CHOICES)

    related_people = SortedMultipleChoiceField(
        label='key people',
        queryset=models.Person.objects.all(),
        required=False,
        widget=SortedFilteredSelectMultiple(attrs={'verbose_name':'person', 'verbose_name_plural':'people'})
    )
    related_groups = forms.ModelMultipleChoiceField(
        queryset=models.Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('groups', False)
    )
    related_locations = forms.ModelMultipleChoiceField(
        queryset=models.Location.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('locations', False)
    )
    related_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('categories', False)
    )


    def __init__(self, *args, **kwargs):
        super(RelatedPeoplePluginForm, self).__init__(*args, **kwargs)
        if 'related_groups' in self.fields and ALDRYN_PEOPLE_HIDE_GROUPS != 0:
            del self.fields['related_groups']
        if 'related_locations' in self.fields and ALDRYN_PEOPLE_HIDE_LOCATION != 0:
            del self.fields['related_locations']
