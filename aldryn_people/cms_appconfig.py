# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_apphooks_config.models import AppHookConfig
from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from sortedm2m.fields import SortedManyToManyField
try:
    from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple, SortedMultipleChoiceField
except:
    from django.contrib.admin.widgets import FilteredSelectMultiple as SortedFilteredSelectMultiple
    SortedMultipleChoiceField = forms.ModelMultipleChoiceField


class PeopleConfig(TranslatableModel, AppHookConfig):
    """Adds some translatable, per-app-instance fields."""
    translations = TranslatedFields(
        app_title=models.CharField(_('name'), max_length=234),
    )
    group = models.ForeignKey('aldryn_people.Group', on_delete=models.CASCADE)

    def get_app_title(self):
        return getattr(self, 'app_title', _('untitled'))

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')

    def __str__(self):
        return self.safe_translation_getter('app_title')


class PeopleConfigForm(AppDataForm):
    pass

setup_config(PeopleConfigForm, PeopleConfig)
