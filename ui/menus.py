# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Menu
from ..core.cache import izom_propui_free_cached_entry_tree_bundle
from ..core.context import izom_propui_free_context_params

from .helpers import (
    _izom_propui_free_active_entry,
    _izom_propui_free_active_layout_view_item,
    _izom_propui_free_layout_item_by_uid,
    _izom_propui_free_layout_item_column_label,
    _izom_propui_free_shared_row_group_size,
)


class IZOM_PROPUI_FREE_MT_active_entry_children(Menu):
    bl_label = "Active Entry Children"
    bl_idname = "IZOM_PROPUI_FREE_MT_active_entry_children"

    def draw(self, context):
        layout = self.layout
        params = izom_propui_free_context_params(context)
        if params is None:
            return

        active_entry = _izom_propui_free_active_entry(context)
        active_uid = str(getattr(active_entry, 'uid', '') or '').strip() if active_entry is not None else ''
        if not active_uid:
            layout.label(text="No Active Entry")
            return

        bundle = izom_propui_free_cached_entry_tree_bundle(params)
        tree_state = bundle.get('tree_state', {}) or {}
        snapshots = bundle.get('entry_snapshots', ()) or ()
        index_by_uid = tree_state.get('index_by_uid', {}) or {}
        child_uids = tuple(tree_state.get('children_by_uid', {}).get(active_uid, ()) or ())
        if not child_uids:
            layout.label(text="No Direct Children")
            return

        for child_uid in child_uids:
            child_index = index_by_uid.get(str(child_uid or '').strip())
            if not isinstance(child_index, int) or not (0 <= child_index < len(snapshots)):
                continue
            child_snapshot = snapshots[child_index]
            child_label = (
                str(child_snapshot.get('label', '') or '').strip()
                or str(child_snapshot.get('prop_id', '') or '').strip()
                or 'Child'
            )
            op = layout.operator(
                "wm.izom_propui_free_select_entry",
                text=child_label,
                icon='DOT',
            )
            op.target_uid = str(child_snapshot.get('uid', '') or '').strip()
            op.editor_context = 'HIERARCHY'


class IZOM_PROPUI_FREE_MT_entry_tools(Menu):
    bl_label = "izom PropUI Entry Tools"
    bl_idname = "IZOM_PROPUI_FREE_MT_entry_tools"

    def draw(self, _context):
        layout = self.layout
        clear_row = layout.row()
        clear_row.operator_context = 'INVOKE_DEFAULT'
        clear_row.operator("wm.izom_propui_free_remove_all_entries", text="Clear Entry List", icon='TRASH')


class IZOM_PROPUI_FREE_MT_layout_tools(Menu):
    bl_label = "izom PropUI Generated Layout Tools"
    bl_idname = "IZOM_PROPUI_FREE_MT_layout_tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.izom_propui_free_import_layout_entries", text="Import", icon='IMPORT')
        params = izom_propui_free_context_params(context)
        if params is not None:
            layout.prop(params, "izom_propui_free_gl_safe_import", text="Safe Import")
        layout.separator()
        clear_row = layout.row()
        clear_row.operator_context = 'INVOKE_DEFAULT'
        clear_row.operator("wm.izom_propui_free_clear_layout_entries", text="Clear Generated Layout", icon='TRASH')


def _izom_propui_free_draw_value_label_tools(layout, target_mode, clear_label):
    sort_options = (
        ('AT_LEAST_DESC', "Sort At Least Rows High to Low"),
        ('AT_MOST_ASC', "Sort At Most Rows Low to High"),
        ('EQUAL_ASC', "Sort Equals Rows Low to High"),
        ('RANGE_NARROW', "Sort Range Rows Narrow First"),
    )
    for sort_mode, label in sort_options:
        op = layout.operator("wm.izom_propui_free_sort_value_labels", text=label)
        op.target_mode = target_mode
        op.sort_mode = sort_mode
    layout.separator()
    row = layout.row()
    row.operator_context = 'INVOKE_DEFAULT'
    op = row.operator("wm.izom_propui_free_clear_value_labels", text=clear_label, icon='TRASH')
    op.target_mode = target_mode


class IZOM_PROPUI_FREE_MT_value_label_tools_self(Menu):
    bl_label = "Dynamic Label Tools"
    bl_idname = "IZOM_PROPUI_FREE_MT_value_label_tools_self"

    def draw(self, _context):
        _izom_propui_free_draw_value_label_tools(self.layout, 'SELF', "Clear Dynamic Labels")


class IZOM_PROPUI_FREE_MT_layout_import(Menu):
    bl_label = "Generated Layout Import"
    bl_idname = "IZOM_PROPUI_FREE_MT_layout_import"

    def draw(self, _context):
        layout = self.layout
        layout.operator("wm.izom_propui_free_import_layout_entries", text="Import", icon='IMPORT')


class IZOM_PROPUI_FREE_MT_layout_column(Menu):
    bl_label = "Generated Layout Column"
    bl_idname = "IZOM_PROPUI_FREE_MT_layout_column"

    def draw(self, context):
        layout = self.layout
        params = izom_propui_free_context_params(context)
        if params is None:
            return
        active_view_item = _izom_propui_free_active_layout_view_item(params)
        if active_view_item is None or str(getattr(active_view_item, 'kind', '') or '').strip() != 'ENTRY_ITEM':
            return
        layout_item = _izom_propui_free_layout_item_by_uid(params, str(getattr(active_view_item, 'layout_uid', '') or '').strip())
        if layout_item is None:
            return
        row_size = _izom_propui_free_shared_row_group_size(params, layout_item=layout_item)
        if row_size <= 1:
            layout.label(text="Single-entry rows stay in Column 1.")
            return
        for column_index in range(1, max(1, int(row_size or 1)) + 1):
            current_label = _izom_propui_free_layout_item_column_label(params, layout_item)
            op = layout.operator(
                "wm.izom_propui_free_set_layout_column",
                text=f"Column {column_index}",
                icon='RADIOBUT_ON' if current_label == str(column_index) else 'RADIOBUT_OFF',
            )
            op.column = str(column_index)


CLASSES = (
    IZOM_PROPUI_FREE_MT_active_entry_children,
    IZOM_PROPUI_FREE_MT_entry_tools,
    IZOM_PROPUI_FREE_MT_layout_tools,
    IZOM_PROPUI_FREE_MT_value_label_tools_self,
    IZOM_PROPUI_FREE_MT_layout_import,
    IZOM_PROPUI_FREE_MT_layout_column,
)
