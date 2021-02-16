# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from six import iteritems

from django.conf import settings
from django.utils.translation import ugettext as _, get_language_from_request
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:
    # Django 2.0
    from django.urls import reverse, NoReverseMatch

from cms.api import get_page_draft
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.cms_toolbars import LANGUAGE_MENU_IDENTIFIER
from cms.utils.urlutils import admin_reverse
from cms.utils.i18n import get_language_tuple, get_language_dict
from menus.utils import DefaultLanguageChanger

from parler.models import TranslatableModel

from .models import Group, Person
from .constants import ALDRYN_PEOPLE_HIDE_GROUPS
from . import DEFAULT_APP_NAMESPACE

ADD_OBJ_LANGUAGE_BREAK = "Add object language Break"

def get_obj_from_request(model, request,
                         pk_url_kwarg='pk',
                         slug_url_kwarg='slug',
                         slug_field='slug'):
    """
    Given a model and the request, try to extract and return an object
    from an available 'pk' or 'slug', or return None.

    Note that no checking is done that the view's kwargs really are for objects
    matching the provided model (how would it?) so use only where appropriate.
    """
    language = get_language_from_request(request, check_path=True)
    kwargs = request.resolver_match.kwargs
    mgr = model.objects
    if pk_url_kwarg in kwargs:
        return mgr.filter(pk=kwargs[pk_url_kwarg]).first()
    elif slug_url_kwarg in kwargs:
        # If the model is translatable, and the given slug is a translated
        # field, then find it the Parler way.
        filter_kwargs = {slug_field: kwargs[slug_url_kwarg]}
        translated_fields = model._parler_meta.get_translated_fields()
        if (issubclass(model, TranslatableModel) and
                slug_url_kwarg in translated_fields):
            return mgr.active_translations(language, **filter_kwargs).first()
        else:
            # OK, do it the normal way.
            return mgr.filter(**filter_kwargs).first()
    else:
        return None


def get_admin_url(action, action_args=[], **url_args):
    """
    Convenience method for constructing admin-urls with GET parameters.
    """
    base_url = admin_reverse(action, args=action_args)
    # Converts [{key: value}, …] => ["key=value", …]
    url_arg_list = sorted(iteritems(url_args))
    params = ["=".join([str(k), str(v)]) for (k, v) in url_arg_list]
    if params:
        return "?".join([base_url, "&".join(params)])
    else:
        return base_url


@toolbar_pool.register
class PeopleToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Person, Group, ]
    supported_apps = ('aldryn_people', )

    def populate(self):
        self.page = get_page_draft(self.request.current_page)
        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if user and view_name:
            obj = None
            language = get_language_from_request(self.request, check_path=True)
            group = person = None
            if view_name == '%s:group-detail' % DEFAULT_APP_NAMESPACE:
                if ALDRYN_PEOPLE_HIDE_GROUPS == 0:
                    group = get_obj_from_request(Group, self.request)
            elif view_name in [
                    '%s:person-detail' % DEFAULT_APP_NAMESPACE,
                    '%s:download_vcard' % DEFAULT_APP_NAMESPACE]:
                obj = get_obj_from_request(Person, self.request)
                if obj and obj.groups:
                    group = obj.primary_group
            elif view_name == '%s:group-list' % DEFAULT_APP_NAMESPACE:
                pass
            else:
                # We don't appear to be on any aldryn_people views so this
                # menu shouldn't even be here.
                return

            menu = self.toolbar.get_or_create_menu('people-app', "People")

            change_group_perm = user.has_perm('aldryn_people.change_group')
            add_group_perm = user.has_perm('aldryn_people.add_group')
            group_perms = [change_group_perm, add_group_perm]

            change_person_perm = user.has_perm('aldryn_people.change_person')
            add_person_perm = user.has_perm('aldryn_people.add_person')
            person_perms = [change_person_perm, add_person_perm]

            if ALDRYN_PEOPLE_HIDE_GROUPS == 0:
                if change_group_perm:
                    url = admin_reverse('aldryn_people_group_changelist')
                    menu.add_sideframe_item(_('Group list'), url=url)

                if add_group_perm:
                    url_args = {}
                    if language:
                        url_args.update({"language": language})
                    url = get_admin_url('aldryn_people_group_add', **url_args)
                    menu.add_modal_item(_('Add new group'), url=url)

                if change_group_perm and group:
                    url = get_admin_url('aldryn_people_group_change', [group.pk, ])
                    menu.add_modal_item(_('Edit group'), url=url, active=True)

                if any(group_perms) and any(person_perms):
                    menu.add_break()

            if change_person_perm:
                url = admin_reverse('aldryn_people_person_changelist')
                menu.add_sideframe_item(_('Person list'), url=url)

            if add_person_perm:
                url_args = {}
                if group:
                    url_args['groups'] = group.pk
                if language:
                    url_args['language'] = language
                url = get_admin_url('aldryn_people_person_add', **url_args)
                menu.add_modal_item(_('Add new person'), url=url)

            if change_person_perm and obj:
                url = admin_reverse(
                    'aldryn_people_person_change', args=(obj.pk, ))
                menu.add_modal_item(_('Edit person'), url=url, active=True)

            if settings.USE_I18N:# and not self._language_menu:
                if obj:
                    self._language_menu = self.toolbar.get_or_create_menu(LANGUAGE_MENU_IDENTIFIER, _('Language'), position=-1)
                    self._language_menu.items = []
                    languages = get_language_dict(self.current_site.pk)
                    page_languages = self.page.get_languages()
                    remove = []

                    for code, name in get_language_tuple():
                        if code in obj.get_available_languages():
                            remove.append((code, name))
                            try:
                                url = obj.get_absolute_url(code)
                            except NoReverseMatch:
                                url = None
                            if url and code in page_languages:
                                self._language_menu.add_link_item(name, url=url, active=self.current_lang == code)

                    if self.toolbar.edit_mode_active:
                        add = [l for l in languages.items() if l not in remove]
                        copy = [(code, name) for code, name in languages.items() if code != self.current_lang and (code, name) in remove]

                        if (add or len(remove) > 1 or copy) and change_person_perm:
                            self._language_menu.add_break(ADD_OBJ_LANGUAGE_BREAK)

                            if add:
                                add_plugins_menu = self._language_menu.get_or_create_menu('{0}-add-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Add Translation'))
                                for code, name in add:
                                    url_args = {}
                                    url = '%s?language=%s' % (get_admin_url('aldryn_people_person_change',
                                        [obj.pk], **url_args), code)
                                    add_plugins_menu.add_modal_item(name, url=url)

                            if len(remove) > 1:
                                remove_plugins_menu = self._language_menu.get_or_create_menu('{0}-del-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Delete Translation'))
                                for code, name in remove:
                                    url = get_admin_url('aldryn_people_person_delete_translation', [obj.pk, code])
                                    remove_plugins_menu.add_modal_item(name, url=url)

                            if copy:
                                copy_plugins_menu = self._language_menu.get_or_create_menu('{0}-copy-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Copy all plugins'))
                                title = _('from %s')
                                question = _('Are you sure you want to copy all plugins from %s?')
                                url = get_admin_url('aldryn_people_person_copy_language', [obj.pk])
                                for code, name in copy:
                                    copy_plugins_menu.add_ajax_item(
                                        title % name, action=url,
                                        data={'source_language': code, 'target_language': self.current_lang},
                                        question=question % name, on_success=self.toolbar.REFRESH_PAGE
                                    )
