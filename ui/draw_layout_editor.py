# SPDX-License-Identifier: GPL-3.0-or-later

from types import SimpleNamespace

import bpy

from .draw_common import (  # noqa: F401
    _izom_propui_free_draw_sub_section,
    _izom_propui_free_template_list_rows,
)
from .editor_sections import izom_propui_free_ordered_editor_subsection_specs
from .helper_layout_lookup import (
    _izom_propui_free_layout_item_by_uid,
    _izom_propui_free_layout_row_by_index,
)
from .helper_layout_rows import (
    _izom_propui_free_layout_row_group_collapsed,
    _izom_propui_free_layout_view_row_member_uids,
)
from .helper_layout_view import _izom_propui_free_active_layout_view_item
from .lists_common_entry_state import izom_propui_free_draw_entry_list_header



def _izom_propui_free_generated_layout_active_view_item(params):
    active_item = _izom_propui_free_active_layout_view_item(params)
    if active_item is None:
        return None
    return active_item


def draw_izom_propui_free_generated_layout_editor(layout, params, *, show_header=True, state_bundle=None):
    _draw_izom_propui_free_generated_layout_editor_inner(
        layout,
        params,
        show_header=show_header,
        state_bundle=state_bundle,
    )


def _draw_izom_propui_free_generated_layout_editor_inner(layout, params, *, show_header=True, state_bundle=None):
    ctx = _izom_propui_free_generated_layout_editor_context(
        layout,
        params,
        show_header=show_header,
        state_bundle=state_bundle,
    )
    _izom_propui_free_draw_generated_layout_header(ctx)
    _izom_propui_free_draw_generated_layout_list(ctx)
    _izom_propui_free_draw_generated_layout_structure_controls(ctx)
    _izom_propui_free_draw_generated_layout_ordered_sections(ctx)
    return ctx.box


def _izom_propui_free_generated_layout_editor_context(layout, params, *, show_header=True, state_bundle=None):
    active_view_item = _izom_propui_free_generated_layout_active_view_item(params)
    active_view_kind = str(getattr(active_view_item, 'kind', '') or '').strip()
    active_view_uid = str(getattr(active_view_item, 'uid', '') or '').strip()
    active_row_group_uid = ''
    if active_view_kind == 'ROW_HEADER':
        active_row_group_uid = active_view_uid
    elif active_view_kind == 'ENTRY_ITEM':
        active_row_group_uid = str(getattr(active_view_item, 'parent_uid', '') or '').strip()
    return SimpleNamespace(
        layout=layout,
        params=params,
        box=layout.box() if show_header else layout.column(),
        show_header=show_header,
        state_bundle=state_bundle,
        hide_selected_row=bool(getattr(params, 'izom_propui_free_hide_generated_layout_selected_row_section', False)),
        active_view_item=active_view_item,
        active_view_kind=active_view_kind,
        active_view_uid=active_view_uid,
        active_row_group_uid=active_row_group_uid,
    )


def _izom_propui_free_draw_generated_layout_header(ctx):
    if ctx.show_header:
        ctx.box.label(text="Generated Layout")


def _izom_propui_free_draw_generated_layout_list(ctx):
    visible_layout_count = len(getattr(ctx.params, 'izom_propui_free_layout_view_items', []) or [])
    layout_rows, layout_maxrows = _izom_propui_free_template_list_rows(
        visible_layout_count,
        preferred_rows=4,
        max_rows=8,
    )
    list_row = ctx.box.row()
    list_row.use_property_split = False
    list_row.use_property_decorate = False
    list_col = list_row.column()
    list_col.use_property_split = False
    list_col.use_property_decorate = False
    izom_propui_free_draw_entry_list_header(list_col, data=ctx.params, context=bpy.context)
    list_col.template_list(
        "IZOM_PROPUI_FREE_UL_layout_entries",
        "",
        ctx.params,
        "izom_propui_free_layout_view_items",
        ctx.params,
        "izom_propui_free_layout_view_active_index",
        rows=layout_rows,
        maxrows=layout_maxrows,
    )
    _izom_propui_free_draw_generated_layout_list_buttons(ctx, list_row.column(align=True))


def _izom_propui_free_draw_generated_layout_list_buttons(ctx, controls):
    op = controls.operator("wm.izom_propui_free_add_entry", icon='ADD', text="")
    op.editor_context = 'LAYOUT'
    op = controls.operator("wm.izom_propui_free_remove_entry", icon='REMOVE', text="")
    op.editor_context = 'LAYOUT'
    op = controls.operator("wm.izom_propui_free_duplicate_entry", icon='DUPLICATE', text="")
    op.editor_context = 'LAYOUT'
    controls.separator()
    op = controls.operator("wm.izom_propui_free_move_entry", icon='TRIA_UP', text="")
    op.direction = 'UP'
    op.editor_context = 'LAYOUT'
    op = controls.operator("wm.izom_propui_free_move_entry", icon='TRIA_DOWN', text="")
    op.direction = 'DOWN'
    op.editor_context = 'LAYOUT'
    controls.separator()
    controls.menu("IZOM_PROPUI_FREE_MT_layout_tools", icon='DOWNARROW_HLT', text="")


def _izom_propui_free_draw_generated_layout_structure_controls(ctx):
    if ctx.active_view_item is None:
        return
    structure_row = ctx.box.row(align=True)
    if ctx.active_view_kind == 'ENTRY_ITEM':
        op = structure_row.operator("wm.izom_propui_free_group_layout_item", icon='TRIA_LEFT', text="")
        op.direction = 'LEFT'
        op = structure_row.operator("wm.izom_propui_free_group_layout_item", icon='TRIA_RIGHT', text="")
        op.direction = 'RIGHT'
    else:
        structure_row.separator()
    _izom_propui_free_draw_generated_layout_collapse_control(ctx, structure_row)
    ungroup_row = structure_row.row(align=True)
    ungroup_row.enabled = ctx.active_view_kind == 'ROW_HEADER'
    ungroup_row.operator("wm.izom_propui_free_ungroup_layout_row", text="Ungroup Row Group")


def _izom_propui_free_draw_generated_layout_collapse_control(ctx, structure_row):
    collapse_row = structure_row.row(align=True)
    collapse_row.enabled = bool(ctx.active_row_group_uid)
    collapse_row.operator(
        "wm.izom_propui_free_toggle_active_layout_row_group_collapse",
        icon=(
            'DISCLOSURE_TRI_RIGHT'
            if _izom_propui_free_layout_row_group_collapsed(ctx.params, ctx.active_row_group_uid) else
            'DISCLOSURE_TRI_DOWN'
        ),
        text="",
    )


def _izom_propui_free_draw_generated_layout_ordered_sections(ctx):
    drawers = {
        'GENERATED_LAYOUT_SELECTED_ROW': _izom_propui_free_draw_generated_layout_selected_row_section,
    }
    for generated_layout_spec in izom_propui_free_ordered_editor_subsection_specs(ctx.params, 'GENERATED_LAYOUT'):
        drawer = drawers.get(str(generated_layout_spec.get('key', '') or '').strip().upper())
        if drawer is not None:
            drawer(ctx)


def _izom_propui_free_draw_generated_layout_selected_row_section(ctx):
    if ctx.hide_selected_row or ctx.active_view_item is None:
        return
    active_row_layout_item = _izom_propui_free_generated_layout_active_row_item(ctx)
    if active_row_layout_item is None:
        return
    _izom_propui_free_draw_generated_layout_selected_row_controls(ctx, active_row_layout_item)


def _izom_propui_free_generated_layout_active_row_item(ctx):
    active_row_layout_uid = ''
    if ctx.active_view_kind == 'ENTRY_ITEM':
        active_row_layout_uid = str(getattr(ctx.active_view_item, 'layout_uid', '') or '').strip()
    elif ctx.active_view_kind == 'ROW_HEADER':
        row_member_uids = _izom_propui_free_layout_view_row_member_uids(ctx.active_view_item)
        active_row_layout_uid = row_member_uids[0] if row_member_uids else ''
    return _izom_propui_free_layout_item_by_uid(ctx.params, active_row_layout_uid)


def _izom_propui_free_draw_generated_layout_selected_row_controls(ctx, active_row_layout_item):
    active_row = _izom_propui_free_layout_row_by_index(
        ctx.params,
        getattr(active_row_layout_item, 'row_index', 1),
    )
    row_settings = _izom_propui_free_draw_sub_section(
        ctx.box,
        ctx.params,
        'izom_propui_free_selected_row_expanded',
        "Selected Row",
        'IPO_EASE_IN_OUT',
    )
    if row_settings is None:
        return
    if active_row is not None:
        _izom_propui_free_draw_generated_layout_row_settings(ctx, row_settings, active_row)
    if ctx.active_view_kind == 'ENTRY_ITEM':
        _izom_propui_free_draw_generated_layout_column_settings(ctx, row_settings, active_row_layout_item)


def _izom_propui_free_draw_generated_layout_row_settings(ctx, row_settings, active_row):
    row_settings.prop(active_row, "row_height_scale", text="Row Height")
    row_settings.separator()
    row_settings.prop(active_row, "row_inset_left_enabled", text="Left Indent")


def _izom_propui_free_draw_generated_layout_column_settings(ctx, row_settings, active_row_layout_item):
    return
