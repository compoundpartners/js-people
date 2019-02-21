# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_client import forms


class Form(forms.BaseForm):
    people_plugin_styles = forms.CharField(
        'List of additional people plugin styles (comma separated)',
        required=False
    )

    user_threshold = forms.NumberField(
        'Once there are this many users, change drop-down to ID input field',
        required=False, min_value=0
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
    hide_groups = forms.CheckboxField(
        'Hide Groups', required=False, initial=False
    )
    hide_location = forms.CheckboxField(
        'Hide Location', required=False, initial=False
    )
    hide_user = forms.CheckboxField(
        'Hide user', required=False, initial=False
    )
    secondary_image = forms.CheckboxField(
        'Show secondary image', required=False, initial=False
    )
    secondary_phone = forms.CheckboxField(
        'Show secondary telephone number', required=False, initial=False
    )
    summary_richtext = forms.CheckboxField(
        "Use rich text for Summary",
        required=False,
        initial=False)

    def to_settings(self, data, settings):
        settings['PEOPLE_PLUGIN_STYLES'] = data.get('people_plugin_styles', '')
        try:
            settings['ALDRYN_PEOPLE_USER_THRESHOLD'] = int(data.get(
                'user_threshold'))
        except (ValueError, TypeError):
            pass
        settings['ALDRYN_PEOPLE_HIDE_FAX'] = int(data['hide_fax'])
        settings['ALDRYN_PEOPLE_HIDE_WEBSITE'] = int(data['hide_website'])
        settings['ALDRYN_PEOPLE_HIDE_FACEBOOK'] = int(data['hide_facebook'])
        settings['ALDRYN_PEOPLE_HIDE_TWITTER'] = int(data['hide_twitter'])
        settings['ALDRYN_PEOPLE_HIDE_LINKEDIN'] = int(data['hide_linkedin'])
        settings['ALDRYN_PEOPLE_HIDE_GROUPS'] = int(data['hide_groups'])
        settings['ALDRYN_PEOPLE_HIDE_LOCATION'] = int(data['hide_location'])
        settings['ALDRYN_PEOPLE_HIDE_USER'] = int(data['hide_user'])
        settings['ALDRYN_PEOPLE_SHOW_SECONDARY_IMAGE'] = int(data['secondary_image'])
        settings['ALDRYN_PEOPLE_SHOW_SECONDARY_PHONE'] = int(data['secondary_phone'])
        settings['ALDRYN_PEOPLE_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])
        settings['INSTALLED_APPS'].append('sortedm2m_filter_horizontal_widget')

        return settings
