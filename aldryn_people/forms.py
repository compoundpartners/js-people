# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import widgets
from aldryn_categories.models import Category
try:
    from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple#, SortedMultipleChoiceField
except:
    SortedFilteredSelectMultiple = FilteredSelectMultiple
    SortedMultipleChoiceField = forms.ModelMultipleChoiceField
from sortedm2m.forms import SortedMultipleChoiceField
from django.utils.safestring import mark_safe
from parler.forms import TranslatableModelForm
from js_services.models import Service
from js_locations.models import Location
from . import models
from . import DEFAULT_APP_NAMESPACE

from .constants import (
    ALDRYN_PEOPLE_HIDE_GROUPS,
    ALDRYN_PEOPLE_HIDE_LOCATION,
    IS_THERE_COMPANIES,
    RELATED_PEOPLE_LAYOUT,
    ALDRYN_PEOPLE_SUMMARY_RICHTEXT,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

STATIC_URL = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)


class PersonAdminForm(TranslatableModelForm):
    companies = forms.CharField(required=False, widget=forms.HiddenInput)
    groups = forms.ModelMultipleChoiceField(
        queryset=models.Group.objects.all().exclude(namespace=DEFAULT_APP_NAMESPACE),
        required=False,
        widget=FilteredSelectMultiple('groups', False)
    )

    #class Meta:
        #model = Person

    def __init__(self, *args, **kwargs):
        super(PersonAdminForm, self).__init__(*args, **kwargs)
        if not ALDRYN_PEOPLE_SUMMARY_RICHTEXT:
            self.fields['description'].widget = widgets.Textarea()
        if IS_THERE_COMPANIES:
            self.fields['companies'] = SortedMultipleChoiceField(queryset=Company.objects.all(), required=False)# self.instance.companies
            self.fields['companies'].widget = SortedFilteredSelectMultiple()
            self.fields['companies'].queryset = Company.objects.all()
            if self.instance.pk and self.instance.companies.count():
                self.fields['companies'].initial = self.instance.sorted_companies


class RelatedPeoplePluginForm(forms.ModelForm):

    layout = forms.ChoiceField(choices=RELATED_PEOPLE_LAYOUT)

    related_people = SortedMultipleChoiceField(
        label='key people',
        queryset=models.Person.objects.all(),
        required=False,
        widget=SortedFilteredSelectMultiple('person', False, attrs={'verbose_name_plural':'people'})
    )
    related_groups = forms.ModelMultipleChoiceField(
        queryset=models.Group.objects.all().exclude(namespace=DEFAULT_APP_NAMESPACE),
        required=False,
        widget=FilteredSelectMultiple('groups', False)
    )
    related_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('locations', False)
    )
    related_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('categories', False)
    )
    related_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('services', False)
    )
    related_companies = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(RelatedPeoplePluginForm, self).__init__(*args, **kwargs)
        if 'related_groups' in self.fields and ALDRYN_PEOPLE_HIDE_GROUPS != 0:
            del self.fields['related_groups']
        if 'related_locations' in self.fields and ALDRYN_PEOPLE_HIDE_LOCATION != 0:
            del self.fields['related_locations']
        if IS_THERE_COMPANIES:
            self.fields['related_companies'] = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), required=False)
            self.fields['related_companies'].widget = SortedFilteredSelectMultiple()
            self.fields['related_companies'].queryset = Company.objects.all()
            if self.instance.pk and self.instance.related_companies.count():
                self.fields['related_companies'].initial = self.instance.related_companies.all()
