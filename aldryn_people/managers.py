# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from parler.managers import TranslatableManager, TranslatableQuerySet

from .constants import (
    TRANSLATE_IS_PUBLISHED,
)


class PublishedQuerySet(TranslatableQuerySet):
    def published(self):
        if TRANSLATE_IS_PUBLISHED:
            return self.translated(is_published_trans=True)
        return self.filter(is_published=True)

    def published_one_of_trans(self):
        if TRANSLATE_IS_PUBLISHED:
            return self.filter(translations__is_published_trans=True)
        return self.published()


class PeopleManager(TranslatableManager):
    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self.db)

    def published(self):
        return self.get_queryset().published()

    def published_one_of_trans(self):
        return self.get_queryset().published_one_of_trans()
