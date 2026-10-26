# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import EnumProperty
from bpy.types import Operator

from .operators_entries_core_common import (
    _izom_propui_free_active_layout_view_layout_uid_fast,
    _izom_propui_free_restore_layout_snapshots,
    _izom_propui_free_set_entry_selection_direct,
    _izom_propui_free_set_layout_view_selection,
    izom_propui_free_snapshot_layout_items,
)
from ..core.cache_state import izom_propui_free_cached_state_bundle
from ..core.constants_types import (
    IZOM_PROPUI_FREE_PROP_TYPE_IDS,
    izom_propui_free_is_managed_prop_type,
)
from ..core.context import izom_propui_free_context_params
from ..core.entry_ids import (
    _izom_propui_free_next_default_entry_n,
    _izom_propui_free_unique_prop_id,
)
from ..core.snapshot_entries_common import _izom_propui_free_make_default_snapshot
from ..core.snapshot_entries_restore import izom_propui_free_restore_entries
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from ..core.snapshot_tree import _izom_propui_free_subtree_end
from .helper_layout_view import _izom_propui_free_active_layout_view_layout_uid
from .helper_selection_common import (
    _izom_propui_free_report_operator,
    _izom_propui_free_set_last_editor_context,
)
from .helper_selection_entries import _izom_propui_free_active_entry_uid
from .operators_entries_shared_common import (
    _izom_propui_free_entry_operator_description,
    _izom_propui_free_selected_root_uids,
)
from .operators_entries_shared_copy import _izom_propui_free_insert_entry_snapshot_direct
from .operators_entries_shared_order import (
    _izom_propui_free_active_entry_uid_direct,
    _izom_propui_free_entry_order_state_direct,
    _izom_propui_free_selected_entry_uids_direct,
)
from .operators_layout_import import (
    _izom_propui_free_append_layout_entry,
    _izom_propui_free_append_layout_entry_live_single_row,
    _izom_propui_free_gl_safe_import_enabled,
    _izom_propui_free_import_entry_into_layout,
)
from .operators_layout_selection import (
    _izom_propui_free_capture_layout_view_selection,
    _izom_propui_free_restore_layout_view_selection,
    _izom_propui_free_restore_layout_view_selection_direct,
)



class IZOM_PROPUI_FREE_OT_add_entry(Operator):
    bl_idname = "wm.izom_propui_free_add_entry"
    bl_label = "Add izom PropUI Entry"
    bl_description = "Insert a new entry after the active entry block, or at the end if nothing is active"
    bl_options = {'UNDO', 'INTERNAL'}

    editor_context: EnumProperty(
        name="Editor Context",
        items=[
            ('HIERARCHY', 'Hierarchy', ''),
            ('LAYOUT', 'Layout', ''),
        ],
        default='HIERARCHY',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        return izom_propui_free_context_params(context) is not None

    @classmethod
    def description(cls, _context, properties):
        return _izom_propui_free_entry_operator_description(
            'add',
            editor_context=getattr(properties, 'editor_context', 'HIERARCHY'),
        )

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        _izom_propui_free_set_last_editor_context(params, self.editor_context)
        if self.editor_context == 'LAYOUT':
            return self._execute_layout_add(params)
        return self._execute_hierarchy_add(params)

    def _execute_layout_add(self, params):
        target_entry_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
        if not target_entry_uid:
            _izom_propui_free_report_operator(self, 'WARNING', 'Select an Entry List entry to import into Generated Layout')
            return {'CANCELLED'}

        safe_import = _izom_propui_free_gl_safe_import_enabled(params)
        state_bundle = izom_propui_free_cached_state_bundle(params)
        if safe_import and target_entry_uid in (state_bundle.get('layout_item_lookup', {}).get('by_entry_uid', {}) or {}):
            _izom_propui_free_report_operator(self, 'INFO', 'Already in Generated Layout')
            return {'FINISHED'}

        layout_snapshots = [dict(snap) for snap in (state_bundle.get('layout_snapshots') or ())]
        inserted_layout = _izom_propui_free_import_entry_into_layout(
            layout_snapshots,
            target_entry_uid,
            after_layout_uid=_izom_propui_free_active_layout_view_layout_uid(params, after=True),
            safe_import=safe_import,
            add_into_active_row=False,
            params=params,
        )
        if inserted_layout is None:
            if safe_import:
                _izom_propui_free_report_operator(self, 'INFO', 'Already in Generated Layout')
                return {'FINISHED'}
            return {'CANCELLED'}
        inserted_layout_uid = str(inserted_layout.get('uid', '') or '').strip()
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=inserted_layout_uid,
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        view_uid = _izom_propui_free_layout_view_entry_uid(inserted_layout_uid)
        _izom_propui_free_set_layout_view_selection(
            params,
            [view_uid],
            active_uid=view_uid,
            anchor_uid=view_uid,
            update_list_context=False,
        )
        return {'FINISHED'}

    def _execute_hierarchy_add(self, params):
        prior_layout_active_uid = str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
        auto_sync_new_entries = False
        prior_layout_view_selection = (
            _izom_propui_free_capture_layout_view_selection(params, validate=False)
            if auto_sync_new_entries else
            None
        )
        default_entry_type = self._default_entry_type(params)
        snapshots, index_by_uid, tree_state, _order = _izom_propui_free_entry_order_state_direct(params)
        new_item = self._new_entry_snapshot(params, snapshots, index_by_uid, default_entry_type)
        insert_index = self._entry_insert_index_and_parent(
            params,
            new_item,
            snapshots,
            index_by_uid,
            tree_state,
        )
        self._insert_new_entry_snapshot(
            params,
            snapshots,
            new_item,
            insert_index,
            prior_layout_active_uid,
        )
        if auto_sync_new_entries:
            self._auto_sync_new_entry_to_layout(params, new_item['uid'], prior_layout_active_uid)
        _izom_propui_free_set_entry_selection_direct(params, new_item['uid'], insert_index)
        if prior_layout_view_selection is not None:
            if not _izom_propui_free_restore_layout_view_selection_direct(params, prior_layout_view_selection):
                _izom_propui_free_restore_layout_view_selection(params, prior_layout_view_selection)
        return {'FINISHED'}

    def _default_entry_type(self, params):
        return 'FLOAT'

    def _new_entry_snapshot(self, params, snapshots, index_by_uid, default_entry_type):
        new_item = _izom_propui_free_make_default_snapshot(_izom_propui_free_next_default_entry_n(snapshots))
        new_item['_live_unique_default_prop_id'] = new_item.get('prop_id', '')
        new_item['prop_type'] = default_entry_type
        return new_item

    def _entry_insert_index_and_parent(self, params, new_item, snapshots, index_by_uid, tree_state):
        selection_active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
        selected_roots = _izom_propui_free_selected_root_uids(
            snapshots,
            _izom_propui_free_selected_entry_uids_direct(params, snapshots, index_by_uid),
            index_by_uid=index_by_uid,
        )
        active_index = index_by_uid.get(selection_active_uid)
        active_snap = snapshots[active_index] if active_index is not None else None
        if selected_roots:
            return self._insert_after_selected_roots(new_item, snapshots, index_by_uid, tree_state, selected_roots, active_snap)
        if active_snap is not None:
            new_item['parent_uid'] = active_snap.get('parent_uid', '')
            return _izom_propui_free_subtree_end(snapshots, active_index, state=tree_state)
        return len(snapshots)

    def _insert_after_selected_roots(self, new_item, snapshots, index_by_uid, tree_state, selected_roots, active_snap):
        insert_index = 0
        for uid in selected_roots:
            start_index = index_by_uid.get(uid)
            if start_index is None:
                continue
            insert_index = max(insert_index, _izom_propui_free_subtree_end(snapshots, start_index, state=tree_state))
        new_item['parent_uid'] = str((active_snap or {}).get('parent_uid', '') or '').strip()
        return insert_index

    def _insert_new_entry_snapshot(self, params, snapshots, new_item, insert_index, prior_layout_active_uid):
        self._ensure_new_entry_prop_id_unique(new_item, snapshots)
        if _izom_propui_free_insert_entry_snapshot_direct(params, new_item, insert_index):
            return
        fallback_snapshots = [dict(snap) for snap in snapshots]
        fallback_snapshots[insert_index:insert_index] = [new_item]
        izom_propui_free_restore_entries(
            params,
            fallback_snapshots,
            active_uid=new_item['uid'],
            layout_active_uid=prior_layout_active_uid,
            preserve_layout_items=True,
        )

    def _ensure_new_entry_prop_id_unique(self, new_item, snapshots):
        live_unique_default_prop_id = str(new_item.pop('_live_unique_default_prop_id', '') or '').strip()
        if not izom_propui_free_is_managed_prop_type(new_item.get('prop_type', 'FLOAT')):
            return

        raw_prop_id = str(new_item.get('prop_id', '') or '').strip() or 'prop'
        if raw_prop_id == live_unique_default_prop_id:
            return

        existing_ids = {
            str((snap or {}).get('prop_id', '') or '').strip()
            for snap in (snapshots or ())
            if izom_propui_free_is_managed_prop_type((snap or {}).get('prop_type', 'FLOAT'))
        }
        existing_ids.discard('')
        new_item['prop_id'] = _izom_propui_free_unique_prop_id(raw_prop_id, existing_ids)

    def _auto_sync_new_entry_to_layout(self, params, entry_uid, prior_layout_active_uid):
        add_into_active_row = False
        after_layout_uid = _izom_propui_free_active_layout_view_layout_uid_fast(params, after=True) or prior_layout_active_uid
        direct_layout_uid = ''
        if not add_into_active_row:
            direct_layout_uid = _izom_propui_free_append_layout_entry_live_single_row(
                params,
                entry_uid,
                after_layout_uid=after_layout_uid,
            )
        if direct_layout_uid:
            return
        layout_snapshots = [dict(snap) for snap in izom_propui_free_snapshot_layout_items(params)]
        _izom_propui_free_append_layout_entry(
            layout_snapshots,
            entry_uid,
            after_layout_uid=after_layout_uid,
            add_into_active_row=add_into_active_row,
            params=params,
        )
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=prior_layout_active_uid,
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
