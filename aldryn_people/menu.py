# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import get_language_from_request, ugettext as _

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import Group, Person
from .constants import ALDRYN_PEOPLE_HIDE_GROUPS


class PersonMenu(CMSAttachMenu):
    """
    Provides an attachable menu of all people.
    """
    name = _('JumpSuite People: Person Menu')

    def get_nodes(self, request):
        nodes = []
        language = get_language_from_request(request, check_path=True)
        persons = (Person.objects.language(language)
                                 .active_translations(language))

        for person in persons:
            try:
                url = person.get_absolute_url(language=language)
            except NoReverseMatch:
                url = None
            if url:
                node = NavigationNode(
                    str(person),
                    url,
                    person.pk,
                )
                nodes.append(node)
        return nodes


menu_pool.register_menu(PersonMenu)


class GroupMenu(CMSAttachMenu):
    """
    Provides an attachable menu of all groups.
    """
    name = _('JumpSuite People: Group Menu')

    def get_nodes(self, request):
        nodes = []
        language = get_language_from_request(request, check_path=True)
        groups = (Group.objects.language(language)
                               .active_translations(language))

        for group in groups:
            try:
                url = group.get_absolute_url(language=language)
            except NoReverseMatch:
                url = None
            if url:
                node = NavigationNode(
                    group.safe_translation_getter(
                        'name', default=_('group: {0}').format(group.pk),
                        language_code=language),
                    url,
                    group.pk,
                )
                nodes.append(node)
        return nodes

#if ALDRYN_PEOPLE_HIDE_GROUPS == 0:
    #menu_pool.register_menu(GroupMenu)
