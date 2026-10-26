# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_entry_layout_common import (
    _izom_propui_free_active_layout_view_item,
)
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator
from ..core.snapshot_layout_common import izom_propui_free_snapshot_layout_items
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from .helper_layout_view import _izom_propui_free_set_layout_view_selection
from .helper_selection_common import (
    _izom_propui_free_set_last_editor_context,
    _izom_propui_free_uid_list_from_json,
)
from .operators_layout_base import _izom_propui_free_entry_params
from .operators_layout_live_groups import (
    _izom_propui_free_group_layout_item_adjacent_row_direct,
    _izom_propui_free_ungroup_layout_row_direct,
)
from .operators_layout_live_members import _izom_propui_free_set_layout_view_row_member_column_direct
from .operators_layout_mutation import (
    _izom_propui_free_group_layout_item_into_next_row,
    _izom_propui_free_group_layout_item_into_previous_row,
    _izom_propui_free_reposition_layout_item_column,
    _izom_propui_free_ungroup_layout_child_to_top_level,
    _izom_propui_free_ungroup_layout_child_to_top_level_before,
    _izom_propui_free_ungroup_layout_row,
)
from .operators_layout_restore_snapshots import _izom_propui_free_restore_layout_snapshots



class IZOM_PROPUI_FREE_OT_set_layout_column(Operator):
    bl_idname = "wm.izom_propui_free_set_layout_column"
    bl_label = "Set Generated Layout Column"
    bl_description = "Place the selected Generated Layout child in the chosen column inside its row"
    bl_options = {'UNDO', 'INTERNAL'}

    column: StringProperty(
        name="Column",
        description="1-based Generated Layout column position inside the current row",
        default='1',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return False
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        return bool(active_view_item and str(getattr(active_view_item, 'kind', '') or '').strip() == 'ENTRY_ITEM')

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        if active_view_item is None:
            return {'CANCELLED'}
        layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
        if not layout_uid:
            return {'CANCELLED'}
        try:
            requested_column = max(1, int(str(self.column or '1').strip() or '1'))
        except (TypeError, ValueError):
            requested_column = 1
        parent_view_uid = str(getattr(active_view_item, 'parent_uid', '') or '').strip()
        if parent_view_uid.startswith('ROW_HEADER:'):
            moved, _view_uid = _izom_propui_free_set_layout_view_row_member_column_direct(
                params,
                active_view_item,
                requested_column,
            )
            if moved:
                return {'FINISHED'}
        layout_snapshots = izom_propui_free_snapshot_layout_items(params)
        if not _izom_propui_free_reposition_layout_item_column(layout_snapshots, layout_uid, requested_column, params=params):
            return {'CANCELLED'}
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=layout_uid,
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        view_uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
        _izom_propui_free_set_layout_view_selection(params, [view_uid], active_uid=view_uid, anchor_uid=view_uid, update_list_context=False)
        return {'FINISHED'}

class IZOM_PROPUI_FREE_OT_group_layout_item(Operator):
    bl_idname = "wm.izom_propui_free_group_layout_item"
    bl_label = "Group Generated Layout Entry"
    bl_description = "Group the selected top-level entry into the Row Group above or below, or ungroup a child above or below its current Row Group"
    bl_options = {'UNDO', 'INTERNAL'}

    direction: EnumProperty(
        name="Direction",
        items=[
            ('LEFT', 'Left', ''),
            ('RIGHT', 'Right', ''),
        ],
        default='RIGHT',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return False
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        return bool(active_view_item and str(getattr(active_view_item, 'kind', '') or '').strip() == 'ENTRY_ITEM')

    @classmethod
    def description(cls, _context, properties):
        direction = str(getattr(properties, 'direction', 'RIGHT') or 'RIGHT').strip().upper()
        if direction == 'LEFT':
            return (
                "Group the selected top-level entry into the Row Group above, or move a grouped child out above its "
                "current Row Group"
            )
        return (
            "Group the selected top-level entry into the Row Group below, or move a grouped child out below its "
            "current Row Group"
        )

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        if active_view_item is None:
            return {'CANCELLED'}
        layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
        if not layout_uid:
            return {'CANCELLED'}
        parent_uid = str(getattr(active_view_item, 'parent_uid', '') or '').strip()
        direction = str(self.direction or 'RIGHT').strip().upper()
        if not parent_uid:
            direct_changed, direct_view_uid = _izom_propui_free_group_layout_item_adjacent_row_direct(
                params,
                active_view_item,
                direction,
            )
            if direct_changed:
                return {'FINISHED'}
        layout_snapshots = izom_propui_free_snapshot_layout_items(params)
        if direction == 'LEFT':
            changed = (
                _izom_propui_free_ungroup_layout_child_to_top_level_before(layout_snapshots, layout_uid, params=params)
                if parent_uid else
                _izom_propui_free_group_layout_item_into_previous_row(layout_snapshots, layout_uid, params=params)
            )
        else:
            changed = (
                _izom_propui_free_ungroup_layout_child_to_top_level(layout_snapshots, layout_uid, params=params)
                if parent_uid else
                _izom_propui_free_group_layout_item_into_next_row(layout_snapshots, layout_uid, params=params)
            )
        if not changed:
            return {'CANCELLED'}
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=layout_uid,
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        view_uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
        _izom_propui_free_set_layout_view_selection(params, [view_uid], active_uid=view_uid, anchor_uid=view_uid, update_list_context=False)
        return {'FINISHED'}

class IZOM_PROPUI_FREE_OT_ungroup_layout_row(Operator):
    bl_idname = "wm.izom_propui_free_ungroup_layout_row"
    bl_label = "Ungroup Generated Layout Row"
    bl_description = (
        "Break the selected Generated Layout row into separate single-entry rows"
    )
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return False
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        return bool(active_view_item and str(getattr(active_view_item, 'kind', '') or '').strip() == 'ROW_HEADER')

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        if active_view_item is None:
            return {'CANCELLED'}
        direct_changed, direct_view_uid = _izom_propui_free_ungroup_layout_row_direct(params, active_view_item)
        if direct_changed:
            return {'FINISHED'}
        row_number = int(getattr(active_view_item, 'row_index', 1) or 1)
        member_uids = _izom_propui_free_uid_list_from_json(getattr(active_view_item, 'row_member_uids_json', '[]'))
        layout_snapshots = izom_propui_free_snapshot_layout_items(params)
        if not _izom_propui_free_ungroup_layout_row(layout_snapshots, row_number, params=params):
            return {'CANCELLED'}
        next_layout_uid = member_uids[0] if member_uids else ''
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=next_layout_uid,
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        next_view_uid = _izom_propui_free_layout_view_entry_uid(next_layout_uid) if next_layout_uid else ''
        _izom_propui_free_set_layout_view_selection(
            params,
            [next_view_uid] if next_view_uid else [],
            active_uid=next_view_uid,
            anchor_uid=next_view_uid,
            update_list_context=False,
        )
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
