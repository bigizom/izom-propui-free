# SPDX-License-Identifier: GPL-3.0-or-later

from .editor_sections import izom_propui_free_ordered_editor_subsection_specs


def _izom_propui_free_draw_reset_settings(column, params):
    if bool(getattr(params, 'izom_propui_free_hide_editor_settings_reset_section', False)):
        return
    box = column.box().column(align=True)
    box.label(text="Reset izom PropUI")
    row = box.row(align=True)
    row.alert = True
    row.operator_context = 'INVOKE_DEFAULT'
    row.operator("wm.izom_propui_free_full_factory_reset", text="Full Factory Reset", icon='TRASH')


def draw_izom_propui_free_editor_settings_section(column, params):
    drawers = {
        'EDITOR_RESET': _izom_propui_free_draw_reset_settings,
    }
    for spec in izom_propui_free_ordered_editor_subsection_specs(params, 'EDITOR_SETTINGS'):
        drawer = drawers.get(str(spec.get('key', '') or '').strip().upper())
        if drawer is not None:
            drawer(column, params)
