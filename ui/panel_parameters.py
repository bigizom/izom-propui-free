# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from ..core.cache import (
    izom_propui_free_cached_entry_navigation_bundle,
    izom_propui_free_cached_layout_bundle,
)
from ..core.diagnostics import izom_propui_free_debug_enabled, izom_propui_free_recent_diagnostics
from .draw import (
    draw_izom_propui_free_hierarchy_editor,
)
from .editor_sections import (
    izom_propui_free_editor_section_is_visible,
    izom_propui_free_normalize_editor_section_key,
)
from .panel_parameters_properties import (
    izom_propui_free_add_panel_parameters,
)
from .panel_parameters_editor_settings import draw_izom_propui_free_editor_settings_section
from .panel_parameters_output_setup import draw_izom_propui_free_output_setup_section
from .draw_entry_settings import draw_izom_propui_free_entry_settings
from .draw_layout_editor import draw_izom_propui_free_generated_layout_editor
from .helper_selection import _izom_propui_free_active_entry



class IzomPropUIPanelParametersMixin:
    @classmethod
    def add_parameters(cls, params):
        izom_propui_free_add_panel_parameters(params)

    @classmethod
    def draw_editor_section_ui(cls, layout, params, section_key):
        cls._draw_editor_sections(
            layout,
            params,
            section_key=izom_propui_free_normalize_editor_section_key(section_key),
        )

    @classmethod
    def _draw_editor_sections(cls, layout, params, *, section_key=''):
        layout.use_property_split = False
        layout.use_property_decorate = False
        col = layout.column()
        if not hasattr(params, 'izom_propui_free_entries') or not hasattr(params, 'izom_propui_free_layout_items'):
            warning = col.box().row(align=True)
            warning.alert = True
            warning.label(text="izom PropUI scene settings are not registered. Disable and re-enable the add-on.", icon='ERROR')
            return

        def draw_diagnostics_body(parent, records):
            diagnostics_col = parent.column(align=True)
            debug_enabled = izom_propui_free_debug_enabled(bpy.context)
            for record in reversed(records):
                level = str(record.get('level', 'WARNING') or 'WARNING').upper()
                icon = 'ERROR' if level == 'ERROR' else 'INFO'
                row = diagnostics_col.row(align=True)
                row.alert = level in {'ERROR', 'WARNING'}
                prefix = f"{record.get('timestamp', '')} {record.get('category', 'General')}:"
                suppressed_count = int(record.get('suppressed_count', 0) or 0)
                suffix = f" (+{suppressed_count} similar)" if suppressed_count else ""
                row.label(text=f"{prefix} {record.get('message', '')}{suffix}", icon=icon)
                row.operator_context = 'INVOKE_DEFAULT'
                details = row.operator("wm.izom_propui_free_diagnostic_details", text='', icon='VIEWZOOM', emboss=False)
                details.text = '\n'.join(
                    str(record.get(key, '') or '')
                    for key in ('timestamp', 'level', 'category', 'message', 'details', 'exception', 'traceback')
                    if record.get(key)
                )

                exception_text = str(record.get('exception', '') or '').strip()
                if debug_enabled and exception_text:
                    diagnostics_col.label(text=exception_text, icon='CONSOLE')
            diagnostics_col.operator("wm.izom_propui_free_clear_diagnostics", icon='TRASH')

        def draw_output_setup(column):
            draw_izom_propui_free_output_setup_section(column, params)

        def draw_selected_entry(column, *, tree_bundle=None):
            active_entry = _izom_propui_free_active_entry(params)
            if active_entry is None:
                return tree_bundle
            if tree_bundle is None:
                tree_bundle = izom_propui_free_cached_entry_navigation_bundle(params, context=bpy.context)
            draw_izom_propui_free_entry_settings(
                column,
                params,
                active_entry,
                state=tree_bundle.get('tree_state', {}),
            )
            return tree_bundle

        def draw_generated_layout(column, *, state_bundle=None):
            if state_bundle is None:
                state_bundle = izom_propui_free_cached_layout_bundle(params, context=bpy.context)
            draw_izom_propui_free_generated_layout_editor(
                column,
                params,
                show_header=False,
                state_bundle=state_bundle,
            )
            return state_bundle

        def draw_editor_settings(column):
            draw_izom_propui_free_editor_settings_section(column, params)

        def draw_diagnostics_panel(column):
            records = izom_propui_free_recent_diagnostics(min_level='WARNING', limit=8)
            if records:
                draw_diagnostics_body(column, records)

        section_drawers = {
            'DIAGNOSTICS': draw_diagnostics_panel,
            'OUTPUT_SETUP': draw_output_setup,
            'ENTRY_LIST': lambda column: draw_izom_propui_free_hierarchy_editor(column, params, show_header=False),
            'SELECTED_ENTRY': draw_selected_entry,
            'GENERATED_LAYOUT': draw_generated_layout,
            'EDITOR_SETTINGS': draw_editor_settings,
        }

        def draw_editor_section_body(column, requested_section_key):
            if not izom_propui_free_editor_section_is_visible(params, requested_section_key):
                return
            drawer = section_drawers.get(requested_section_key)
            if drawer is not None:
                drawer(column)

        requested_section_key = izom_propui_free_normalize_editor_section_key(section_key)
        if requested_section_key:
            draw_editor_section_body(col, requested_section_key)
