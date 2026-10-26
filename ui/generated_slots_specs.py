# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.constants_display import IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB


def _izom_propui_free_generated_slot_space_types(_slot):
    return ('VIEW_3D',)


def _izom_propui_free_generated_slot_panel_specs(slot):
    return [{
        'location': 'SIDEBAR',
        'space_type': 'VIEW_3D',
        'region_type': 'UI',
        'context_id': '',
        'bl_context': '',
        'tab': str((slot or {}).get('tab', '') or '').strip() or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    }]


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
