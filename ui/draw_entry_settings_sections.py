# SPDX-License-Identifier: GPL-3.0-or-later


IZOM_PROPUI_FREE_ENTRY_SETTINGS_SECTION_SPECS = (
    {
        'key': 'basics',
        'hide_attr': 'izom_propui_free_hide_selected_basics_section',
        'expanded_attr': '',
        'title': 'Basics',
        'icon': 'DOT',
    },
    {
        'key': 'value',
        'hide_attr': 'izom_propui_free_hide_selected_value_section',
        'expanded_attr': 'izom_propui_free_custom_prop_expanded',
        'title': 'Value',
        'icon': 'PROPERTIES',
    },
    {
        'key': 'display',
        'hide_attr': 'izom_propui_free_hide_selected_display_section',
        'expanded_attr': 'izom_propui_free_display_expanded',
        'title': 'Display',
        'icon': 'WINDOW',
    },
    {
        'key': 'dynamic_labels',
        'hide_attr': 'izom_propui_free_hide_selected_dynamic_labels_section',
        'expanded_attr': 'izom_propui_free_copy_settings_expanded',
        'title': 'Dynamic Labels',
        'icon': 'SORTSIZE',
    },
    {
        'key': 'conditions',
        'hide_attr': 'izom_propui_free_hide_selected_conditions_section',
        'expanded_attr': 'izom_propui_free_child_behavior_expanded',
        'title': 'Conditions',
        'icon': 'CON_CHILDOF',
    },
    {
        'key': 'storage',
        'hide_attr': 'izom_propui_free_hide_selected_storage_section',
        'expanded_attr': 'izom_propui_free_storage_expanded',
        'title': 'Storage',
        'icon': 'LINKED',
    },
)
IZOM_PROPUI_FREE_ENTRY_SETTINGS_SECTION_BY_KEY = {
    spec['key']: spec
    for spec in IZOM_PROPUI_FREE_ENTRY_SETTINGS_SECTION_SPECS
}


def _izom_propui_free_entry_settings_hidden_flags(params):
    return {
        spec['key']: bool(getattr(params, spec['hide_attr'], False))
        for spec in IZOM_PROPUI_FREE_ENTRY_SETTINGS_SECTION_SPECS
    }


def _izom_propui_free_entry_settings_section_spec(key):
    return IZOM_PROPUI_FREE_ENTRY_SETTINGS_SECTION_BY_KEY[str(key or '')]
