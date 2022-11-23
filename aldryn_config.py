# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_client import forms


class Form(forms.BaseForm):
    hide_suffix = forms.CheckboxField(
        'Hide Suffix', required=False, initial=False
    )
    summary_richtext = forms.CheckboxField(
        "Use rich text for Summary",
        required=False,
        initial=False,
    )
    secondary_image = forms.CheckboxField(
        'Show secondary image', required=False, initial=False
    )

    secondary_phone = forms.CheckboxField(
        'Show secondary telephone number', required=False, initial=False
    )
    hide_email = forms.CheckboxField(
        'Hide Email', required=False, initial=False
    )
    hide_mobile = forms.CheckboxField(
        'Hide Mobile', required=False, initial=False
    )
    hide_phone = forms.CheckboxField(
        'Hide Phone', required=False, initial=False
    )
    hide_fax = forms.CheckboxField(
        'Hide Fax', required=False, initial=False
    )
    hide_website = forms.CheckboxField(
        'Hide Website', required=False, initial=False
    )
    hide_facebook = forms.CheckboxField(
        'Hide Facebook', required=False, initial=False
    )
    hide_twitter = forms.CheckboxField(
        'Hide Twitter', required=False, initial=False
    )
    hide_linkedin = forms.CheckboxField(
        'Hide LinkedIn', required=False, initial=False
    )
    hide_xing = forms.CheckboxField(
        'Hide Xing', required=False, initial=False
    )
    hide_vcard = forms.CheckboxField(
        'Hide vCard', required=False, initial=False
    )

    hide_groups = forms.CheckboxField(
        'Hide Groups', required=False, initial=False
    )
    hide_categories = forms.CheckboxField(
        'Hide Categoies', required=False, initial=False
    )
    hide_location = forms.CheckboxField(
        'Hide Location', required=False, initial=False
    )
    hide_user = forms.CheckboxField(
        'Hide user', required=False, initial=False
    )
    translate_is_published = forms.CheckboxField(
        'Translate show on website field', required=False, initial=False
    )
    translate_visual = forms.CheckboxField(
        'Translate people visuals', required=False, initial=False
    )
    people_plugin_styles = forms.CharField(
        'List of additional people plugin styles (comma separated)',
        required=False
    )

    user_threshold = forms.NumberField(
        'Once there are this many users, change drop-down to ID input field',
        required=False, min_value=0
    )

    def to_settings(self, data, settings):
        settings['PEOPLE_PLUGIN_STYLES'] = data.get('people_plugin_styles', '')
        try:
            settings['ALDRYN_PEOPLE_USER_THRESHOLD'] = int(data.get(
                'user_threshold'))
        except (ValueError, TypeError):
            pass
        settings['ALDRYN_PEOPLE_HIDE_EMAIL'] = int(data['hide_email'])
        settings['ALDRYN_PEOPLE_HIDE_PHONE'] = int(data['hide_phone'])
        settings['ALDRYN_PEOPLE_HIDE_MOBILE'] = int(data['hide_mobile'])
        settings['ALDRYN_PEOPLE_HIDE_VCARD'] = int(data['hide_vcard'])
        settings['ALDRYN_PEOPLE_HIDE_SUFFIX'] = int(data['hide_suffix'])
        settings['ALDRYN_PEOPLE_HIDE_FAX'] = int(data['hide_fax'])
        settings['ALDRYN_PEOPLE_HIDE_WEBSITE'] = int(data['hide_website'])
        settings['ALDRYN_PEOPLE_HIDE_FACEBOOK'] = int(data['hide_facebook'])
        settings['ALDRYN_PEOPLE_HIDE_TWITTER'] = int(data['hide_twitter'])
        settings['ALDRYN_PEOPLE_HIDE_LINKEDIN'] = int(data['hide_linkedin'])
        settings['ALDRYN_PEOPLE_HIDE_XING'] = int(data['hide_xing'])
        settings['ALDRYN_PEOPLE_HIDE_GROUPS'] = int(data['hide_groups'])
        settings['ALDRYN_PEOPLE_HIDE_LOCATION'] = int(data['hide_location'])
        settings['ALDRYN_PEOPLE_HIDE_USER'] = int(data['hide_user'])
        settings['ALDRYN_PEOPLE_HIDE_CATEGORIES'] = int(data['hide_categories'])
        settings['ALDRYN_PEOPLE_SHOW_SECONDARY_IMAGE'] = int(data['secondary_image'])
        settings['ALDRYN_PEOPLE_SHOW_SECONDARY_PHONE'] = int(data['secondary_phone'])
        settings['ALDRYN_PEOPLE_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])
        settings['ALDRYN_PEOPLE_TRANSLATE_IS_PUBLISHED'] = int(data['translate_is_published'])
        settings['ALDRYN_PEOPLE_TRANSLATE_VISUAL'] = int(data['translate_visual'])
        settings['INSTALLED_APPS'].append('sortedm2m_filter_horizontal_widget')
        settings['INSTALLED_APPS'].append('django_filters')
        settings['INSTALLED_APPS'].append('crispy_forms')

        return settings
