# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import izom_propui_free_recent_diagnostics
from .helper_selection import _izom_propui_free_active_entry


IZOM_PROPUI_FREE_EDITOR_SECTION_SPECS = (
    {
        'key': 'DIAGNOSTICS',
        'label': 'Diagnostics',
        'hide_prop': '',
        'requires': 'WARNINGS',
        'icon': 'ERROR',
    },
    {
        'key': 'OUTPUT_SETUP',
        'label': 'Output Setup',
        'hide_prop': '',
        'requires': '',
        'icon': 'PROPERTIES',
    },
    {
        'key': 'ENTRY_LIST',
        'label': 'Entry List',
        'hide_prop': '',
        'requires': '',
        'icon': 'OUTLINER_COLLECTION',
    },
    {
        'key': 'SELECTED_ENTRY',
        'label': 'Selected Entry',
        'hide_prop': '',
        'requires': 'ACTIVE_ENTRY',
        'icon': 'RESTRICT_SELECT_OFF',
    },
    {
        'key': 'GENERATED_LAYOUT',
        'label': 'Generated Layout',
        'hide_prop': '',
        'requires': '',
        'icon': 'SORTSIZE',
    },
    {
        'key': 'EDITOR_SETTINGS',
        'label': 'Editor Settings',
        'hide_prop': '',
        'requires': '',
        'icon': 'PREFERENCES',
    },
)


IZOM_PROPUI_FREE_EDITOR_SUBSECTION_SPECS_BY_PARENT = {
    'OUTPUT_SETUP': (
        {
            'key': 'OUTPUT_GENERATE_CONTROLS',
            'label': 'Generate Controls',
            'hide_prop': '',
            'icon': 'PLAY',
        },
        {
            'key': 'OUTPUT_BRANDING',
            'label': 'Generated UI Identity',
            'hide_prop': '',
            'icon': 'FILE_SCRIPT',
        },
        {
            'key': 'OUTPUT_STORAGE',
            'label': 'Property Storage',
            'hide_prop': '',
            'icon': 'LINKED',
        },
    ),
    'ENTRY_LIST': (),
    'SELECTED_ENTRY': (
        {
            'key': 'SELECTED_BASICS',
            'label': 'Basics',
            'hide_prop': '',
            'icon': 'DOT',
        },
        {
            'key': 'SELECTED_VALUE',
            'label': 'Value',
            'hide_prop': '',
            'icon': 'PROPERTIES',
        },
        {
            'key': 'SELECTED_DISPLAY',
            'label': 'Display',
            'hide_prop': '',
            'icon': 'WINDOW',
        },
        {
            'key': 'SELECTED_DYNAMIC_LABELS',
            'label': 'Dynamic Labels',
            'hide_prop': '',
            'icon': 'SORTSIZE',
        },
        {
            'key': 'SELECTED_CONDITIONS',
            'label': 'Conditions',
            'hide_prop': '',
            'icon': 'CON_CHILDOF',
        },
        {
            'key': 'SELECTED_STORAGE',
            'label': 'Storage',
            'hide_prop': '',
            'icon': 'LINKED',
        },
    ),
    'GENERATED_LAYOUT': (
        {
            'key': 'GENERATED_LAYOUT_SELECTED_ROW',
            'label': 'Selected Row',
            'hide_prop': '',
            'icon': 'IPO_EASE_IN_OUT',
        },
    ),
    'EDITOR_SETTINGS': (
        {
            'key': 'EDITOR_RESET',
            'label': 'Reset izom PropUI',
            'hide_prop': '',
            'icon': 'TRASH',
        },
    ),
}


_IZOM_PROPUI_FREE_EDITOR_SECTION_SPEC_BY_KEY = {
    spec['key']: dict(spec, order=index, parent_key='', depth=0)
    for index, spec in enumerate(IZOM_PROPUI_FREE_EDITOR_SECTION_SPECS)
}


def izom_propui_free_normalize_editor_section_key(section_key):
    return str(section_key or '').strip().upper()


def izom_propui_free_editor_section_spec(section_key):
    return _IZOM_PROPUI_FREE_EDITOR_SECTION_SPEC_BY_KEY.get(
        izom_propui_free_normalize_editor_section_key(section_key)
    )


def izom_propui_free_ordered_editor_section_specs(_params=None):
    return tuple(dict(spec, order=index, parent_key='', depth=0) for index, spec in enumerate(IZOM_PROPUI_FREE_EDITOR_SECTION_SPECS))


def izom_propui_free_ordered_editor_subsection_specs(_params, parent_key):
    normalized_parent = izom_propui_free_normalize_editor_section_key(parent_key)
    parent_depth = int(_IZOM_PROPUI_FREE_EDITOR_SECTION_SPEC_BY_KEY.get(normalized_parent, {}).get('depth', 0) or 0)
    return tuple(
        dict(spec, order=index, parent_key=normalized_parent, depth=parent_depth + 1, requires='')
        for index, spec in enumerate(IZOM_PROPUI_FREE_EDITOR_SUBSECTION_SPECS_BY_PARENT.get(normalized_parent, ()))
    )


def izom_propui_free_editor_section_is_visible(params, section_key):
    spec = izom_propui_free_editor_section_spec(section_key)
    if spec is None or params is None:
        return False
    requirement = str(spec.get('requires', '') or '').strip().upper()
    if requirement == 'WARNINGS':
        return bool(izom_propui_free_recent_diagnostics(min_level='WARNING', limit=1))
    if requirement == 'ACTIVE_ENTRY':
        return _izom_propui_free_active_entry(params) is not None
    return True


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
