# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from .operators_entries_core_common import (
    _izom_propui_free_restore_layout_snapshots,
    _izom_propui_free_set_entry_selection_direct,
    _izom_propui_free_set_layout_view_selection,
    _izom_propui_free_uid_list_from_json,
    izom_propui_free_snapshot_layout_items,
)
from ..core.context import izom_propui_free_context_params
from ..core.snapshot_tree import (
    _izom_propui_free_move_block_down,
    _izom_propui_free_move_block_up,
    _izom_propui_free_subtree_end,
)
from .helper_layout_view import (
    _izom_propui_free_active_layout_view_item,
    _izom_propui_free_active_layout_view_layout_uid,
    _izom_propui_free_layout_view_item_by_uid,
)
from .helper_selection_common import _izom_propui_free_set_last_editor_context
from .helper_selection_entries import _izom_propui_free_set_entry_selection
from .operators_entries_shared_common import (
    _izom_propui_free_entry_operator_description,
    _izom_propui_free_selected_root_uids,
)
from .operators_entries_shared_order import (
    _izom_propui_free_active_entry_uid_direct,
    _izom_propui_free_entry_order_state_direct,
    _izom_propui_free_selected_entry_uids_direct,
)
from .operators_entries_shared_structure import (
    _izom_propui_free_move_entry_block_and_update_fields_direct,
    _izom_propui_free_reorder_entry_collection_direct,
    _izom_propui_free_restore_entries_preserving_layout,
)
from .operators_layout_base import _izom_propui_free_snapshot_index_by_uid
from .operators_layout_live_members import _izom_propui_free_move_layout_view_row_member_direct
from .operators_layout_mutation import _izom_propui_free_move_layout_view_item_one_level



class IZOM_PROPUI_FREE_OT_move_entry(Operator):
    bl_idname = "wm.izom_propui_free_move_entry"
    bl_label = "Move izom PropUI Entry"
    bl_description = "Move the selected izom PropUI item"
    bl_options = {'UNDO', 'INTERNAL'}

    direction: EnumProperty(
        name="Direction",
        description="Direction to move the selected izom PropUI item",
        items=[
            ('UP', 'Up', 'Move the selected property entry (with its children) up'),
            ('DOWN', 'Down', 'Move the selected property entry (with its children) down'),
        ],
        default='UP',
    )
    editor_context: EnumProperty(
        name="Editor Context",
        items=[
            ('HIERARCHY', 'Hierarchy', ''),
            ('LAYOUT', 'Layout', ''),
        ],
        default='HIERARCHY',
        options={'HIDDEN'},
    )
    target_view_uid: StringProperty(name="Target View UID", default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        if params is None:
            return False
        return bool(
            len(getattr(params, 'izom_propui_free_entries', []) or []) > 1
            or len(getattr(params, 'izom_propui_free_layout_items', []) or []) > 1
            or len(getattr(params, 'izom_propui_free_layout_view_items', []) or []) > 1
        )

    @classmethod
    def description(cls, _context, properties):
        return _izom_propui_free_entry_operator_description(
            'move',
            editor_context=getattr(properties, 'editor_context', 'HIERARCHY'),
            direction=getattr(properties, 'direction', 'UP'),
        )

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        _izom_propui_free_set_last_editor_context(params, self.editor_context)
        if self.editor_context == 'LAYOUT':
            return self._execute_layout_move(params)
        return self._execute_hierarchy_move(params)

    def _execute_layout_move(self, params):
        target_view_uid = str(getattr(self, 'target_view_uid', '') or '').strip()
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        if active_view_item is None and target_view_uid:
            active_view_item = _izom_propui_free_layout_view_item_by_uid(params, target_view_uid)
        if active_view_item is None:
            return {'CANCELLED'}

        selected_view_uid = str(getattr(active_view_item, 'uid', '') or '').strip()
        active_kind = str(getattr(active_view_item, 'kind', '') or '').strip()

        active_layout_uid = self._active_layout_uid_for_view_item(params, active_view_item, active_kind)
        if active_kind != 'ROW_HEADER':
            direct_moved, _direct_restore_view_uid = _izom_propui_free_move_layout_view_row_member_direct(
                params,
                active_view_item,
                self.direction,
            )
            if direct_moved:
                return {'FINISHED'}

        layout_snapshots = izom_propui_free_snapshot_layout_items(params)
        moved, restore_view_uid = _izom_propui_free_move_layout_view_item_one_level(
            layout_snapshots,
            active_view_item,
            self.direction,
            params=params,
        )
        if not moved:
            return {'CANCELLED'}
        active_layout_uid = active_layout_uid or _izom_propui_free_active_layout_view_layout_uid(params)
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=active_layout_uid,
            sync_view_selection=False,
        )
        restore_uid = restore_view_uid or selected_view_uid
        _izom_propui_free_set_layout_view_selection(
            params,
            [restore_uid],
            active_uid=restore_uid,
            anchor_uid=restore_uid,
            update_list_context=False,
        )
        return {'FINISHED'}

    def _active_layout_uid_for_view_item(self, _params, active_view_item, active_kind):
        if active_kind == 'ROW_HEADER':
            row_members = _izom_propui_free_uid_list_from_json(
                getattr(active_view_item, 'row_member_uids_json', '[]')
            )
            return row_members[0] if row_members else ''
        return str(getattr(active_view_item, 'layout_uid', '') or '').strip()

    def _execute_hierarchy_move(self, params):
        snapshots, index_by_uid, tree_state, _order = _izom_propui_free_entry_order_state_direct(params)
        selected_uids = set(_izom_propui_free_selected_entry_uids_direct(params, snapshots, index_by_uid))
        roots = self._hierarchy_move_roots(params, snapshots, index_by_uid, selected_uids)
        if not roots:
            return {'CANCELLED'}

        moved_any, single_root_direct_move = self._move_hierarchy_roots(
            snapshots,
            index_by_uid,
            tree_state,
            roots,
        )
        if not moved_any:
            return {'CANCELLED'}

        post_index_by_uid = _izom_propui_free_snapshot_index_by_uid(snapshots)
        active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, post_index_by_uid)
        self._apply_hierarchy_move(
            params,
            snapshots,
            active_uid,
            single_root_direct_move,
        )
        self._restore_hierarchy_move_selection(
            params,
            snapshots,
            post_index_by_uid,
            selected_uids,
            active_uid,
        )
        return {'FINISHED'}

    def _hierarchy_move_roots(self, params, snapshots, index_by_uid, selected_uids):
        roots = _izom_propui_free_selected_root_uids(
            snapshots,
            selected_uids,
            index_by_uid=index_by_uid,
        )
        if roots:
            return roots
        active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
        return [active_uid] if active_uid else []

    def _move_hierarchy_roots(self, snapshots, index_by_uid, tree_state, roots):
        moved_any = False
        single_root_direct_move = None
        ordered_roots = roots if self.direction == 'UP' else list(reversed(roots))
        single_ordered_root = len(ordered_roots) == 1
        for root_index, uid in enumerate(ordered_roots):
            if root_index > 0:
                index_by_uid = _izom_propui_free_snapshot_index_by_uid(snapshots)
            index = index_by_uid.get(uid)
            if index is None:
                continue
            move_state = tree_state if len(ordered_roots) == 1 else None
            moved, direct_move = self._move_single_hierarchy_root(
                snapshots,
                index,
                move_state,
                single_ordered_root,
            )
            moved_any = moved_any or moved
            if direct_move is not None:
                single_root_direct_move = direct_move
        return moved_any, single_root_direct_move

    def _move_single_hierarchy_root(self, snapshots, index, move_state, single_ordered_root):
        if single_ordered_root and move_state:
            return self._move_single_root_with_sibling_state(snapshots, index, move_state)
        moved = (
            _izom_propui_free_move_block_up(snapshots, index, state=move_state)
            if self.direction == 'UP'
            else _izom_propui_free_move_block_down(snapshots, index, state=move_state)
        )
        return moved, None

    def _move_single_root_with_sibling_state(self, snapshots, index, move_state):
        parent_uid = str((move_state.get('snapshots', snapshots)[index] or {}).get('parent_uid', '') or '').strip()
        block_end = _izom_propui_free_subtree_end(snapshots, index, state=move_state)
        block_len = max(0, block_end - index)
        if self.direction == 'UP':
            return self._move_single_root_up(snapshots, index, block_end, block_len, parent_uid, move_state)
        return self._move_single_root_down(snapshots, index, block_end, block_len, parent_uid, move_state)

    def _move_single_root_up(self, snapshots, index, block_end, block_len, parent_uid, move_state):
        insert_index = None
        state_snapshots = move_state.get('snapshots', snapshots)
        for cursor in range(index - 1, -1, -1):
            if str((state_snapshots[cursor] or {}).get('parent_uid', '') or '').strip() == parent_uid:
                insert_index = cursor
                break
        if insert_index is None:
            return False, None
        block = snapshots[index:block_end]
        del snapshots[index:block_end]
        snapshots[insert_index:insert_index] = block
        return True, (index, block_len, insert_index)

    def _move_single_root_down(self, snapshots, index, block_end, block_len, parent_uid, move_state):
        next_sibling_index = None
        cursor = block_end
        state_snapshots = move_state.get('snapshots', snapshots)
        while cursor < len(state_snapshots):
            if str((state_snapshots[cursor] or {}).get('parent_uid', '') or '').strip() == parent_uid:
                next_sibling_index = cursor
                break
            cursor += 1
        if next_sibling_index is None:
            return False, None
        next_sibling_end = _izom_propui_free_subtree_end(snapshots, next_sibling_index, state=move_state)
        block = snapshots[index:block_end]
        del snapshots[index:block_end]
        insert_index = next_sibling_end - block_len
        snapshots[insert_index:insert_index] = block
        return True, (index, block_len, insert_index)

    def _apply_hierarchy_move(self, params, snapshots, active_uid, single_root_direct_move):
        direct_applied = False
        if single_root_direct_move is not None:
            move_start, move_len, move_insert = single_root_direct_move
            direct_applied = _izom_propui_free_move_entry_block_and_update_fields_direct(
                params,
                move_start,
                move_len,
                move_insert,
            )
        if direct_applied:
            return
        if _izom_propui_free_reorder_entry_collection_direct(
            params,
            [str(snap.get('uid', '') or '').strip() for snap in snapshots],
            refresh_names=False,
        ):
            return
        _izom_propui_free_restore_entries_preserving_layout(
            params,
            snapshots,
            focus_context='HIERARCHY',
            focus_uid=active_uid,
        )

    def _restore_hierarchy_move_selection(self, params, snapshots, post_index_by_uid, selected_uids, active_uid):
        if len(selected_uids) <= 1:
            next_index = post_index_by_uid.get(active_uid, 0)
            _izom_propui_free_set_entry_selection_direct(params, active_uid, next_index)
            return
        ordered_selection = [
            str(snap.get('uid', '') or '').strip()
            for snap in snapshots
            if str(snap.get('uid', '') or '').strip() in selected_uids
        ]
        _izom_propui_free_set_entry_selection(
            params,
            ordered_selection if ordered_selection else ([active_uid] if active_uid else []),
            active_uid=active_uid,
            anchor_uid=active_uid,
            editor_context=self.editor_context,
            update_list_context=False,
        )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
