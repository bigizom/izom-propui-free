# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from .draw_common import (
    _izom_propui_free_entry_by_uid,
    _izom_propui_free_template_list_rows,
    izom_propui_free_log_recovered,
)
from .helper_selection_entries import _izom_propui_free_active_entry_uid
from .lists_common_entry_state import izom_propui_free_draw_entry_list_header


def _izom_propui_free_active_entry_from_params(params):
    entries = getattr(params, 'izom_propui_free_entries', None)
    if not entries:
        return None
    active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY', persist=False)
    active_entry = _izom_propui_free_entry_by_uid(params, active_uid)
    if active_entry is not None:
        return active_entry
    try:
        active_index = int(getattr(params, 'izom_propui_free_active_index', 0) or 0)
    except (RuntimeError, ValueError, TypeError, AttributeError, ReferenceError, LookupError) as exc:
        izom_propui_free_log_recovered(category='UI', exception=exc)
        active_index = 0
    active_index = max(0, min(active_index, len(entries) - 1))
    try:
        return entries[active_index]
    except (IndexError, TypeError):
        return None


def draw_izom_propui_free_hierarchy_editor(layout, params, *, show_header=True):
    entries_collection = getattr(params, 'izom_propui_free_entries', None)
    box = layout.box() if show_header else layout.column()
    entry_count = len(entries_collection) if entries_collection is not None else 0
    active_entry = _izom_propui_free_active_entry_from_params(params)
    if show_header:
        box.label(text="Entry List")
    entry_rows, entry_maxrows = _izom_propui_free_template_list_rows(
        entry_count,
        preferred_rows=4,
        max_rows=8,
        min_rows=1,
    )

    list_row = box.row()
    list_col = list_row.column()
    list_row.use_property_split = False
    list_row.use_property_decorate = False
    list_col.use_property_split = False
    list_col.use_property_decorate = False
    izom_propui_free_draw_entry_list_header(list_col, data=params, context=bpy.context)
    list_col.template_list(
        "IZOM_PROPUI_FREE_UL_entries",
        "izom_propui_free_entries_tree",
        params,
        "izom_propui_free_entries",
        params,
        "izom_propui_free_active_index",
        rows=entry_rows,
        maxrows=entry_maxrows,
    )

    controls = list_row.column(align=True)
    op = controls.operator("wm.izom_propui_free_add_entry", icon='ADD', text="")
    op.editor_context = 'HIERARCHY'
    op = controls.operator("wm.izom_propui_free_remove_entry", icon='REMOVE', text="")
    op.editor_context = 'HIERARCHY'
    op = controls.operator("wm.izom_propui_free_duplicate_entry", icon='DUPLICATE', text="")
    op.editor_context = 'HIERARCHY'
    controls.separator()
    op = controls.operator("wm.izom_propui_free_move_entry", icon='TRIA_UP', text="")
    op.direction = 'UP'
    op.editor_context = 'HIERARCHY'
    op = controls.operator("wm.izom_propui_free_move_entry", icon='TRIA_DOWN', text="")
    op.direction = 'DOWN'
    op.editor_context = 'HIERARCHY'
    controls.menu("IZOM_PROPUI_FREE_MT_entry_tools", icon='DOWNARROW_HLT', text="")

    structure = box.row(align=True)
    structure.enabled = active_entry is not None
    structure.menu("IZOM_PROPUI_FREE_MT_set_parent", text="Set Parent", icon='NODETREE')
    structure.operator("wm.izom_propui_free_indent_entry", icon='TRIA_LEFT', text="")
    structure.operator("wm.izom_propui_free_outdent_entry", icon='TRIA_RIGHT', text="")
    structure.operator("wm.izom_propui_free_clear_parent", icon='UNLINKED', text="")
    return box


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
