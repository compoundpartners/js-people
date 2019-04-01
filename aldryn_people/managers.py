# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

from parler.managers import TranslatableManager, TranslatableQuerySet


class PublishedQuerySet(TranslatableQuerySet):
    def published(self):
        return self.filter(is_published=True)


class PeopleManager(TranslatableManager):
    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self.db)

    def published(self):
        return self.get_queryset().published()

