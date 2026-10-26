# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Operator

from .operators_entry_hierarchy_common import (
    _izom_propui_free_active_hierarchy_snapshot_info,
    _izom_propui_free_build_state_from_snapshots,
    _izom_propui_free_hierarchy_working_state,
    _izom_propui_free_previous_sibling_uid_from_state,
    _izom_propui_free_snapshot_parent_uid,
    _izom_propui_free_top_ancestor_uid_from_state,
)
from ..core.constants_display import IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH
from ..core.snapshot_tree import _izom_propui_free_subtree_end
from .helper_selection_common import (
    _izom_propui_free_report_operator,
    _izom_propui_free_set_last_editor_context,
)
from .helper_selection_entries import (
    _izom_propui_free_active_entry_uid,
    _izom_propui_free_selected_entry_uids,
    _izom_propui_free_set_entry_selection,
)
from .operators_entries_shared_common import (
    _izom_propui_free_active_snapshot_index,
    _izom_propui_free_entry_target_depth,
    _izom_propui_free_selected_root_uids,
)
from .operators_entries_shared_copy import _izom_propui_free_set_entry_selection_direct
from .operators_entries_shared_structure import (
    _izom_propui_free_apply_entry_structure_snapshots_direct,
    _izom_propui_free_move_entry_block_and_update_fields_direct,
    _izom_propui_free_restore_entries_preserving_layout,
    _izom_propui_free_update_entry_structure_fields_direct,
)
from .operators_layout_base import (
    _izom_propui_free_entry_params,
    _izom_propui_free_snapshot_index_by_uid,
)



class IZOM_PROPUI_FREE_OT_clear_parent(Operator):
    bl_idname = "wm.izom_propui_free_clear_parent"
    bl_label = "Clear Parent"
    bl_description = "Clear the parent relationship for the selected entries"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(params and getattr(params, 'izom_propui_free_entries', None))

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if not params:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, 'HIERARCHY')
        _bundle, snapshots, initial_state = _izom_propui_free_hierarchy_working_state(params)
        if not snapshots:
            return {'CANCELLED'}
        roots = _izom_propui_free_selected_root_uids(
            snapshots,
            _izom_propui_free_selected_entry_uids(params, editor_context='HIERARCHY'),
        )
        if not roots:
            active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
            if active_uid:
                roots = [active_uid]
            else:
                return {'CANCELLED'}
        changed = False
        indexed_roots = []
        current_index_by_uid = initial_state.get('index_by_uid', {}) or _izom_propui_free_snapshot_index_by_uid(snapshots)
        for uid in roots:
            index = current_index_by_uid.get(uid)
            if index is not None:
                indexed_roots.append((index, uid))

        state = initial_state or _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
        single_indexed_root = len(indexed_roots) == 1
        single_root_new_index = None
        single_root_direct_move = None
        changed_uids = set()
        for _original_index, uid in sorted(indexed_roots, reverse=True):
            index = state['index_by_uid'].get(uid)
            if index is None:
                continue
            parent_uid = _izom_propui_free_snapshot_parent_uid(snapshots[index])
            if not parent_uid:
                continue

            top_ancestor_uid = _izom_propui_free_top_ancestor_uid_from_state(
                snapshots,
                state['index_by_uid'],
                uid,
            )
            if not top_ancestor_uid or top_ancestor_uid == uid:
                snapshots[index]['parent_uid'] = ''
                changed = True
                changed_uids.add(uid)
                if single_indexed_root:
                    single_root_new_index = index
                else:
                    state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
                continue

            ancestor_index = state['index_by_uid'].get(top_ancestor_uid)
            if ancestor_index is None:
                continue
            ancestor_end = _izom_propui_free_subtree_end(snapshots, ancestor_index, state=state)
            block_end = _izom_propui_free_subtree_end(snapshots, index, state=state)
            block = snapshots[index:block_end]
            if not block:
                continue
            block_len = len(block)
            del snapshots[index:block_end]
            block[0]['parent_uid'] = ''
            changed_uids.add(uid)
            insert_index = max(0, min(len(snapshots), ancestor_end - block_len))
            snapshots[insert_index:insert_index] = block
            changed = True
            if single_indexed_root:
                single_root_new_index = insert_index
                single_root_direct_move = (index, block_len, insert_index)
            else:
                state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
        if not changed:
            return {'CANCELLED'}
        active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
        direct_applied = False
        if single_indexed_root and len(changed_uids) == 1:
            changed_uid = next(iter(changed_uids))
            if single_root_direct_move is not None:
                move_start, move_len, move_insert = single_root_direct_move
                direct_applied = _izom_propui_free_move_entry_block_and_update_fields_direct(
                    params,
                    move_start,
                    move_len,
                    move_insert,
                    field_values_by_uid={changed_uid: {'parent_uid': ''}},
                )
            else:
                direct_applied = _izom_propui_free_update_entry_structure_fields_direct(
                    params,
                    {changed_uid: {'parent_uid': ''}},
                )
        if not direct_applied and not _izom_propui_free_apply_entry_structure_snapshots_direct(
            params,
            snapshots,
            field_names=('parent_uid',),
            field_update_uids=changed_uids,
        ):
            _izom_propui_free_restore_entries_preserving_layout(
                params,
                snapshots,
                focus_context='HIERARCHY',
                focus_uid=active_uid,
            )
        selection_active_uid = active_uid if active_uid in roots else (roots[-1] if roots else active_uid)
        if len(roots) == 1 and selection_active_uid:
            next_index = (
                single_root_new_index
                if single_root_new_index is not None and selection_active_uid == roots[0]
                else _izom_propui_free_snapshot_index_by_uid(snapshots).get(selection_active_uid, 0)
            )
            _izom_propui_free_set_entry_selection_direct(params, selection_active_uid, next_index)
        else:
            _izom_propui_free_set_entry_selection(
                params,
                roots,
                active_uid=selection_active_uid,
                anchor_uid=roots[0] if roots else active_uid,
                editor_context='HIERARCHY',
            )
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_indent_entry(Operator):
    bl_idname = "wm.izom_propui_free_indent_entry"
    bl_label = "Make Child Of Previous"
    bl_description = "Make the selected entry a child of its previous sibling"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return False
        bundle, snapshots, _index_by_uid, index, active_uid = _izom_propui_free_active_hierarchy_snapshot_info(params)
        if len(snapshots) <= 1:
            return False
        if index <= 0 or not active_uid:
            return False
        tree_state = bundle.get('tree_state', {}) if isinstance(bundle, dict) else {}
        return bool(_izom_propui_free_previous_sibling_uid_from_state(tree_state, active_uid))

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _bundle, snapshots, state = _izom_propui_free_hierarchy_working_state(params)
        if not state:
            state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
        active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
        index = state.get('index_by_uid', {}).get(active_uid) if active_uid else None
        if index is None:
            index = _izom_propui_free_active_snapshot_index(params, snapshots, editor_context='HIERARCHY')
        if index <= 0:
            return {'CANCELLED'}

        active_uid = str(snapshots[index].get('uid', '') or '').strip()
        previous_uid = _izom_propui_free_previous_sibling_uid_from_state(state, active_uid)

        if not previous_uid:
            return {'CANCELLED'}
        target_depth = _izom_propui_free_entry_target_depth(state, previous_uid)
        if target_depth > IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH:
            _izom_propui_free_report_operator(
                self,
                'WARNING',
                f'Maximum Entry List depth is {IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH}',
            )
            return {'CANCELLED'}

        snapshots[index]['parent_uid'] = previous_uid
        changed_fields = ('parent_uid',)
        direct_field_values = {'parent_uid': previous_uid}
        if not _izom_propui_free_update_entry_structure_fields_direct(
            params,
            {active_uid: direct_field_values},
        ) and not _izom_propui_free_apply_entry_structure_snapshots_direct(
            params,
            snapshots,
            field_names=changed_fields,
            field_update_uids={active_uid},
        ):
            _izom_propui_free_restore_entries_preserving_layout(
                params,
                snapshots,
                focus_context='HIERARCHY',
                focus_uid=active_uid,
            )
        _izom_propui_free_set_entry_selection_direct(params, active_uid, index)
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_outdent_entry(Operator):
    bl_idname = "wm.izom_propui_free_outdent_entry"
    bl_label = "Outdent Entry"
    bl_description = "Move the selected entry out one parent level"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return False
        _bundle, snapshots, _index_by_uid, index, _active_uid = _izom_propui_free_active_hierarchy_snapshot_info(params)
        if index < 0 or not snapshots:
            return False
        return bool(str(snapshots[index].get('parent_uid', '') or '').strip())

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _bundle, snapshots, state = _izom_propui_free_hierarchy_working_state(params)
        if not state:
            state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
        active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
        index = state.get('index_by_uid', {}).get(active_uid) if active_uid else None
        if index is None:
            index = _izom_propui_free_active_snapshot_index(params, snapshots, editor_context='HIERARCHY')
        if index < 0:
            return {'CANCELLED'}
        active_uid = snapshots[index]['uid']
        parent_uid = snapshots[index]['parent_uid']
        if not parent_uid:
            return {'CANCELLED'}

        parent_index = state['index_by_uid'][parent_uid]
        parent_parent_uid = snapshots[parent_index]['parent_uid']
        snapshots[index]['parent_uid'] = parent_parent_uid

        block_end = _izom_propui_free_subtree_end(snapshots, index, state=state)
        block = snapshots[index:block_end]
        block_len = len(block)
        parent_end = _izom_propui_free_subtree_end(snapshots, parent_index, state=state)
        del snapshots[index:block_end]
        insert_index = max(0, min(len(snapshots), parent_end - block_len))
        snapshots[insert_index:insert_index] = block
        if not _izom_propui_free_move_entry_block_and_update_fields_direct(
            params,
            index,
            block_len,
            insert_index,
            field_values_by_uid={active_uid: {'parent_uid': parent_parent_uid}},
        ) and not _izom_propui_free_apply_entry_structure_snapshots_direct(
            params,
            snapshots,
            field_names=('parent_uid',),
            field_update_uids={active_uid},
        ):
            _izom_propui_free_restore_entries_preserving_layout(
                params,
                snapshots,
                focus_context='HIERARCHY',
                focus_uid=active_uid,
            )
        _izom_propui_free_set_entry_selection_direct(params, active_uid, insert_index)
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
