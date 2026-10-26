# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import StringProperty
from bpy.types import Menu, Operator

from .operators_entry_hierarchy_common import (
    _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE,
    _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE_LIMIT,
    _izom_propui_free_build_state_from_snapshots,
    _izom_propui_free_hierarchy_light_tree,
    _izom_propui_free_parent_menu_tree,
    _izom_propui_free_set_parent_items_cache_key,
)
from ..core.constants_display import IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH
from ..core.context import izom_propui_free_context_params
from ..core.entry_ids import _izom_propui_free_entry_label
from ..core.snapshot_tree import (
    _izom_propui_free_descendant_uids,
    _izom_propui_free_subtree_end,
)
from .helper_selection_common import _izom_propui_free_report_operator
from .operators_entries_shared_common import (
    _izom_propui_free_entry_target_depth,
)
from .operators_entries_shared_copy import _izom_propui_free_set_entry_selection_direct
from .operators_entries_shared_structure import (
    _izom_propui_free_apply_entry_structure_snapshots_direct,
    _izom_propui_free_move_entry_block_and_update_fields_direct,
    _izom_propui_free_restore_entries_preserving_layout,
)



def _izom_propui_free_set_parent_target_items(context):
    fallback = [('', 'None', 'Make this entry a top-level entry', 0)]
    params = izom_propui_free_context_params(context)
    if params is None:
        return fallback
    cache_key = _izom_propui_free_set_parent_items_cache_key(params)
    cached_items = _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE.get(cache_key) if cache_key is not None else None
    if cached_items is not None:
        return cached_items
    snapshots, state, label_by_uid = _izom_propui_free_parent_menu_tree(params)
    if not snapshots:
        return fallback
    active_index = max(0, min(getattr(params, 'izom_propui_free_active_index', 0), len(snapshots) - 1))
    active_uid = snapshots[active_index].get('uid', '')
    invalid = {active_uid} | _izom_propui_free_descendant_uids(snapshots, active_uid, state=state)
    depth_by_uid = state.get('depth_by_uid', {}) if isinstance(state, dict) else {}
    items = [('', 'None', 'Make this entry a top-level entry', 0)]
    item_index = 1
    for snap in snapshots:
        uid = snap.get('uid', '')
        if uid in invalid:
            continue
        if int(depth_by_uid.get(uid, 0) or 0) + 1 > IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH:
            continue
        depth = depth_by_uid.get(uid, 0)
        entry_label = label_by_uid.get(uid) or _izom_propui_free_entry_label(snap)
        label = ("    " * depth) + entry_label
        desc = f"Make this entry a child of {entry_label}"
        items.append((uid, label, desc, item_index))
        item_index += 1
    if cache_key is not None:
        if len(_IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE) >= _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE_LIMIT:
            _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE.clear()
        items = tuple(items)
        _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE[cache_key] = items
    return items


class IZOM_PROPUI_FREE_MT_set_parent(Menu):
    bl_idname = "IZOM_PROPUI_FREE_MT_set_parent"
    bl_label = "Set Parent"

    def draw(self, context):
        layout = self.layout
        for uid, label, desc, _index in _izom_propui_free_set_parent_target_items(context):
            op = layout.operator(
                "wm.izom_propui_free_set_parent",
                text=label,
                icon='UNLINKED' if not uid else 'NODETREE',
            )
            op.target_uid = uid
            if desc:
                op.description = desc


class IZOM_PROPUI_FREE_OT_set_parent(Operator):
    bl_idname = "wm.izom_propui_free_set_parent"
    bl_label = "Set izom PropUI Parent"
    bl_description = "Assign a parent entry directly from a list of valid izom PropUI entries"
    bl_options = {'UNDO', 'INTERNAL'}

    target_uid: StringProperty(
        name="Parent",
        description="Entry UID to use as the new parent",
        default="",
        options={'HIDDEN'},
    )
    description: StringProperty(default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params and len(params.izom_propui_free_entries) > 0)

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        source_snapshots, _entry_by_uid, initial_state = _izom_propui_free_hierarchy_light_tree(
            params,
            copy_snapshots=False,
            include_value_fields=False,
        )
        if not source_snapshots:
            return {'CANCELLED'}
        snapshots = list(source_snapshots)
        index = max(0, min(params.izom_propui_free_active_index, len(snapshots) - 1))
        active_uid = str(snapshots[index].get('uid', '') or '').strip()
        if not initial_state:
            initial_state = _izom_propui_free_build_state_from_snapshots(source_snapshots)
        block_end = _izom_propui_free_subtree_end(snapshots, index, state=initial_state)
        block = [dict(snap) for snap in snapshots[index:block_end]]
        block_uid_set = {
            str((snap or {}).get('uid', '') or '').strip()
            for snap in block
            if str((snap or {}).get('uid', '') or '').strip()
        }
        block_size = max(0, block_end - index)
        del snapshots[index:block_end]
        block[0]['parent_uid'] = self.target_uid or ''

        if self.target_uid:
            target_index = initial_state.get('index_by_uid', {}).get(self.target_uid)
            if target_index is None or self.target_uid in block_uid_set:
                self.report({'ERROR'}, 'Chosen parent entry is no longer available')
                return {'CANCELLED'}
            if _izom_propui_free_entry_target_depth(initial_state, self.target_uid) > IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH:
                _izom_propui_free_report_operator(
                    self,
                    'WARNING',
                    f'Maximum Entry List depth is {IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH}',
                )
                return {'CANCELLED'}
            changed_fields = ('parent_uid',)
            target_end = _izom_propui_free_subtree_end(source_snapshots, target_index, state=initial_state)
            insert_index = target_end - block_size if index < target_end else target_end
            insert_index = max(0, min(insert_index, len(snapshots)))
        else:
            changed_fields = ('parent_uid',)
            insert_index = min(index, len(snapshots))

        snapshots[insert_index:insert_index] = block
        direct_field_values = {'parent_uid': self.target_uid or ''}
        if not _izom_propui_free_move_entry_block_and_update_fields_direct(
            params,
            index,
            block_size,
            insert_index,
            field_values_by_uid={active_uid: direct_field_values},
        ):
            full_snapshots, _entry_by_uid, _full_state = _izom_propui_free_hierarchy_light_tree(
                params,
                copy_snapshots=True,
                include_value_fields=True,
            )
            if full_snapshots:
                full_snapshots = list(full_snapshots)
                full_block = [dict(snap) for snap in full_snapshots[index:block_end]]
                del full_snapshots[index:block_end]
                if full_block:
                    full_block[0]['parent_uid'] = self.target_uid or ''
                full_snapshots[insert_index:insert_index] = full_block
            else:
                full_snapshots = snapshots
            if not _izom_propui_free_apply_entry_structure_snapshots_direct(
                params,
                full_snapshots,
                field_names=changed_fields,
                field_update_uids={active_uid},
            ):
                _izom_propui_free_restore_entries_preserving_layout(
                    params,
                    full_snapshots,
                    focus_context='HIERARCHY',
                    focus_uid=active_uid,
                )
        _izom_propui_free_set_entry_selection_direct(params, active_uid, insert_index)
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
