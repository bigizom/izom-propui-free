# SPDX-License-Identifier: GPL-3.0-or-later

from .editor_sections import izom_propui_free_ordered_editor_subsection_specs
from .target_picker import draw_izom_propui_free_target_picker


def _izom_propui_free_draw_expanding_box(parent, params, prop_name, title):
    section_box = parent.box()
    header = section_box.row(align=True)
    expanded = bool(getattr(params, prop_name, False))
    section_icon = 'TRIA_DOWN' if expanded else 'TRIA_RIGHT'
    toggle = header.operator(
        "wm.izom_propui_free_toggle_editor_expanded",
        text=title,
        icon=section_icon,
        emboss=False,
    )
    toggle.property_name = prop_name
    if not expanded:
        return section_box, header, None
    return section_box, header, section_box.column(align=True)


def _izom_propui_free_draw_output_generate_controls(output_col, params):
    if bool(getattr(params, 'izom_propui_free_hide_output_generate_controls', False)):
        return
    generate_row = output_col.row(align=True)
    generate_row.scale_y = 1.2
    generate_row.operator_context = 'INVOKE_DEFAULT'
    generate_row.operator("wm.izom_propui_free_generate_ui", text="Generate UI", icon='PLAY')
    output_col.separator(factor=0.5)


def _izom_propui_free_draw_output_branding_section(output_col, params):
    branding_col = None
    if not bool(getattr(params, 'izom_propui_free_hide_output_branding_section', False)):
        _branding_box, _branding_header, branding_col = _izom_propui_free_draw_expanding_box(
            output_col,
            params,
            "izom_propui_free_output_setup_branding_expanded",
            "Generated UI Identity",
        )
    if branding_col is None:
        return
    branding_col.prop(params, "izom_propui_free_generated_panel_tab", text="Sidebar Tab")
    branding_col.prop(params, "izom_propui_free_generated_panel_title", text="Panel Title")


def _izom_propui_free_draw_output_storage_section(output_col, params):
    target_col = None
    if not bool(getattr(params, 'izom_propui_free_hide_output_storage_section', False)):
        _target_box, _target_header, target_col = _izom_propui_free_draw_expanding_box(
            output_col,
            params,
            "izom_propui_free_output_setup_storage_expanded",
            "Property Storage",
        )
    if target_col is None:
        return
    draw_izom_propui_free_target_picker(
        target_col,
        params,
        "izom_propui_free_default_target",
        path_attr="izom_propui_free_default_target_owner_path",
        label="Property Storage",
        show_context_buttons=True,
    )
    target_col.prop(params, 'izom_propui_free_replace_storage_on_generate')
    target_col.prop(params, 'izom_propui_free_clean_old_targets_on_generate')
    if params.izom_propui_free_replace_storage_on_generate:
        warning = target_col.column(align=True)
        warning.alert = True
        warning.label(text='Replaces ALL custom properties on this object.', icon='ERROR')


def draw_izom_propui_free_output_setup_section(column, params):
    output_col = column.column(align=True)
    output_drawers = {
        'OUTPUT_GENERATE_CONTROLS': lambda: _izom_propui_free_draw_output_generate_controls(output_col, params),
        'OUTPUT_BRANDING': lambda: _izom_propui_free_draw_output_branding_section(output_col, params),
        'OUTPUT_STORAGE': lambda: _izom_propui_free_draw_output_storage_section(output_col, params),
    }
    for output_spec in izom_propui_free_ordered_editor_subsection_specs(params, 'OUTPUT_SETUP'):
        drawer = output_drawers.get(str(output_spec.get('key', '') or '').strip().upper())
        if drawer is not None:
            drawer()
    transfer_box = output_col.box()
    transfer_box.label(text='Setup Transfer', icon='FILE')
    file_row = transfer_box.row(align=True)
    file_row.operator('wm.izom_propui_free_export_setup_json', text='Export', icon='EXPORT')
    file_row.operator('wm.izom_propui_free_import_setup_json', text='Import', icon='IMPORT')
    clipboard_row = transfer_box.row(align=True)
    clipboard_row.operator('wm.izom_propui_free_copy_setup_json', text='Copy JSON', icon='COPYDOWN')
    clipboard_row.operator('wm.izom_propui_free_paste_setup_json', text='Paste JSON', icon='PASTEDOWN')
    note = transfer_box.column(align=True)
    note.scale_y = 0.8
    note.label(text='Imports compatible Full, Free, and Rigify setup data.', icon='INFO')
    note.label(text='Unsupported paid-edition features are reported and skipped.')


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
