# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import EnumProperty
from bpy.types import Operator

from .operators_entries_core_common import (
    _izom_propui_free_assign_duplicate_prop_ids,
    _izom_propui_free_copy_snapshot_block,
    _izom_propui_free_duplicate_active_leaf_entry_direct,
    _izom_propui_free_insert_entry_snapshot_block_direct,
    _izom_propui_free_restore_layout_snapshots,
    _izom_propui_free_set_entry_selection_direct,
    _izom_propui_free_set_layout_view_selection,
    _izom_propui_free_snapshot_entry,
    izom_propui_free_snapshot_layout_items,
)
from ..core.snapshot_layout_ensure import (
    _izom_propui_free_layout_view_entry_uid,
    _izom_propui_free_layout_view_row_uid,
)
from ..core.snapshot_tree import _izom_propui_free_subtree_end
from .helper_layout_view import _izom_propui_free_active_layout_view_item
from .helper_selection_common import (
    _izom_propui_free_report_operator,
    _izom_propui_free_set_last_editor_context,
)
from .helper_selection_entries import (
    _izom_propui_free_active_entry_uid,
    _izom_propui_free_set_entry_selection,
)
from .operators_entries_shared_common import (
    _izom_propui_free_entry_operator_description,
    _izom_propui_free_selected_root_uids,
)
from .operators_entries_shared_order import (
    _izom_propui_free_active_entry_uid_direct,
    _izom_propui_free_entry_order_state_direct,
    _izom_propui_free_selected_entry_uids_direct,
)
from .operators_entries_shared_structure import _izom_propui_free_restore_entries_preserving_layout
from .operators_layout_base import _izom_propui_free_entry_params
from .operators_layout_import import (
    _izom_propui_free_append_layout_entries,
    _izom_propui_free_append_layout_entry,
    _izom_propui_free_gl_add_into_active_row_enabled,
    _izom_propui_free_gl_auto_sync_enabled,
    _izom_propui_free_gl_safe_import_enabled,
)
from .operators_layout_mutation import _izom_propui_free_duplicate_layout_row



class IZOM_PROPUI_FREE_OT_duplicate_entry(Operator):
    bl_idname = "wm.izom_propui_free_duplicate_entry"
    bl_label = "Duplicate izom PropUI Entries"
    bl_description = "Duplicate the selected izom PropUI item"
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
        params = _izom_propui_free_entry_params(context)
        return bool(params and getattr(params, 'izom_propui_free_entries', None))

    @classmethod
    def description(cls, _context, properties):
        return _izom_propui_free_entry_operator_description(
            'duplicate',
            editor_context=getattr(properties, 'editor_context', 'HIERARCHY'),
        )

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if not params:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, self.editor_context)
        if self.editor_context == 'LAYOUT':
            return self._execute_layout_duplicate(params)
        return self._execute_hierarchy_duplicate(params)

    def _execute_layout_duplicate(self, params):
        layout_snapshots = izom_propui_free_snapshot_layout_items(params)
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        if active_view_item is None:
            return {'CANCELLED'}

        active_kind = str(getattr(active_view_item, 'kind', '') or '').strip()
        if _izom_propui_free_gl_safe_import_enabled(params):
            _izom_propui_free_report_operator(
                self,
                'INFO',
                'Safe Import is on; duplicate Generated Layout entries were skipped',
            )
            return {'FINISHED'}
        if active_kind == 'ROW_HEADER':
            return self._duplicate_layout_row(params, layout_snapshots, active_view_item)
        return self._duplicate_layout_entry(params, layout_snapshots, active_view_item)

    def _duplicate_layout_row(self, params, layout_snapshots, active_view_item):
        duplicated_layout_uids = _izom_propui_free_duplicate_layout_row(
            layout_snapshots,
            int(getattr(active_view_item, 'row_index', 1) or 1),
            params=params,
        )
        if not duplicated_layout_uids:
            return {'CANCELLED'}
        header_view_uid = _izom_propui_free_layout_view_row_uid(duplicated_layout_uids)
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=duplicated_layout_uids[0],
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        _izom_propui_free_set_layout_view_selection(
            params,
            [header_view_uid],
            active_uid=header_view_uid,
            anchor_uid=header_view_uid,
            update_list_context=False,
        )
        return {'FINISHED'}

    def _duplicate_layout_entry(self, params, layout_snapshots, active_view_item):
        active_layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
        if not active_layout_uid:
            return {'CANCELLED'}

        duplicated_layout_uids = []
        insert_after_layout_uid = active_layout_uid
        snapshot_by_uid = {
            str(snap.get('uid', '') or '').strip(): snap
            for snap in layout_snapshots
            if str(snap.get('uid', '') or '').strip()
        }
        for layout_uid in [active_layout_uid]:
            source_snapshot = snapshot_by_uid.get(layout_uid)
            if source_snapshot is None:
                continue
            inserted_layout = _izom_propui_free_append_layout_entry(
                layout_snapshots,
                str(source_snapshot.get('entry_uid', '') or '').strip(),
                after_layout_uid=insert_after_layout_uid,
                add_into_active_row=_izom_propui_free_gl_add_into_active_row_enabled(params),
            )
            insert_after_layout_uid = str(inserted_layout.get('uid', '') or '').strip()
            if insert_after_layout_uid:
                duplicated_layout_uids.append(insert_after_layout_uid)
        if not duplicated_layout_uids:
            return {'CANCELLED'}

        active_duplicate_uid = duplicated_layout_uids[-1]
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=active_duplicate_uid,
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        view_uid = _izom_propui_free_layout_view_entry_uid(active_duplicate_uid)
        _izom_propui_free_set_layout_view_selection(
            params,
            [view_uid],
            active_uid=view_uid,
            anchor_uid=view_uid,
            update_list_context=False,
        )
        return {'FINISHED'}

    def _execute_hierarchy_duplicate(self, params):
        prior_layout_active_uid = str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
        auto_sync = _izom_propui_free_gl_auto_sync_enabled(params)
        if not auto_sync:
            duplicated_leaf_uid = _izom_propui_free_duplicate_active_leaf_entry_direct(params)
            if duplicated_leaf_uid:
                return {'FINISHED'}

        layout_snapshots = izom_propui_free_snapshot_layout_items(params) if auto_sync else []
        snapshots, index_by_uid, state, _order = _izom_propui_free_entry_order_state_direct(params)
        selection_active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
        selected = self._duplicate_source_roots(params, snapshots, index_by_uid)
        if not selected:
            return {'CANCELLED'}

        blocks, selected_roots = self._duplicate_snapshot_blocks(
            params,
            snapshots,
            index_by_uid,
            state,
            selected,
        )
        if not blocks:
            return {'CANCELLED'}

        _izom_propui_free_assign_duplicate_prop_ids(blocks, snapshots)
        insertion_start = self._duplicate_insertion_start(
            snapshots,
            index_by_uid,
            selection_active_uid,
            selected_roots,
        )
        duplicated_snapshots, duplicated_roots = self._flatten_duplicate_blocks(blocks)
        active_uid = duplicated_roots[-1] if duplicated_roots else _izom_propui_free_active_entry_uid(
            params,
            editor_context=self.editor_context,
        )
        self._insert_duplicate_snapshots(
            params,
            snapshots,
            duplicated_snapshots,
            insertion_start,
            active_uid,
        )
        if auto_sync:
            self._sync_duplicated_entries_to_layout(
                params,
                layout_snapshots,
                duplicated_roots,
                prior_layout_active_uid,
            )
        self._restore_duplicate_selection(
            params,
            duplicated_roots,
            active_uid,
            insertion_start,
        )
        return {'FINISHED'}

    def _duplicate_source_roots(self, params, snapshots, index_by_uid):
        selected = _izom_propui_free_selected_root_uids(
            snapshots,
            _izom_propui_free_selected_entry_uids_direct(params, snapshots, index_by_uid),
            index_by_uid=index_by_uid,
        )
        if selected:
            return selected
        active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
        return [active_uid] if active_uid else []

    def _duplicate_snapshot_blocks(self, params, snapshots, index_by_uid, state, selected):
        live_entries = getattr(params, 'izom_propui_free_entries', None) or ()
        try:
            live_entry_count = len(live_entries)
        except TypeError:
            live_entry_count = 0
        blocks = []
        selected_roots = []
        for uid in selected:
            block = self._snapshot_block_for_duplicate(
                snapshots,
                index_by_uid,
                state,
                live_entries,
                live_entry_count,
                uid,
            )
            if block:
                blocks.append(_izom_propui_free_copy_snapshot_block(block))
            selected_roots.append(uid)
        return blocks, selected_roots

    def _snapshot_block_for_duplicate(self, snapshots, index_by_uid, state, live_entries, live_entry_count, uid):
        start_index = index_by_uid.get(uid)
        if start_index is None:
            return []
        end_index = _izom_propui_free_subtree_end(snapshots, start_index, state=state)
        block = []
        for snap_index, snap in enumerate(snapshots[start_index:end_index], start=start_index):
            live_entry = self._live_entry_for_snapshot(
                live_entries,
                live_entry_count,
                snap_index,
                str(snap.get('uid', '') or '').strip(),
            )
            if live_entry is not None:
                block.append(_izom_propui_free_snapshot_entry(live_entry))
        return block

    def _live_entry_for_snapshot(self, live_entries, live_entry_count, snap_index, snap_uid):
        if 0 <= snap_index < live_entry_count:
            candidate = live_entries[snap_index]
            if str(getattr(candidate, 'uid', '') or '').strip() == snap_uid:
                return candidate
        for candidate in live_entries:
            if str(getattr(candidate, 'uid', '') or '').strip() == snap_uid:
                return candidate
        return None

    def _duplicate_insertion_start(self, snapshots, index_by_uid, selection_active_uid, selected_roots):
        insertion_anchor_uid = str(selection_active_uid or (selected_roots[0] if selected_roots else '') or '').strip()
        insertion_start = index_by_uid.get(insertion_anchor_uid)
        if insertion_start is None and selected_roots:
            insertion_start = index_by_uid.get(selected_roots[0])
        if insertion_start is None:
            insertion_start = max(0, len(snapshots) - 1)
        return insertion_start

    def _flatten_duplicate_blocks(self, blocks):
        duplicated_roots = []
        duplicated_snapshots = []
        for block in blocks:
            if not block:
                continue
            duplicated_snapshots.extend(block)
            duplicated_roots.append(str(block[0].get('uid', '') or '').strip())
        return duplicated_snapshots, duplicated_roots

    def _insert_duplicate_snapshots(self, params, snapshots, duplicated_snapshots, insertion_start, active_uid):
        insert_index = insertion_start + 1
        if _izom_propui_free_insert_entry_snapshot_block_direct(params, duplicated_snapshots, insert_index):
            return
        fallback_snapshots = [dict(snap) for snap in snapshots]
        fallback_snapshots[insert_index:insert_index] = duplicated_snapshots
        _izom_propui_free_restore_entries_preserving_layout(
            params,
            fallback_snapshots,
            focus_context='HIERARCHY',
            focus_uid=active_uid,
        )

    def _sync_duplicated_entries_to_layout(self, params, layout_snapshots, duplicated_roots, prior_layout_active_uid):
        inserted_layouts = _izom_propui_free_append_layout_entries(
            layout_snapshots,
            duplicated_roots,
            after_layout_uid=prior_layout_active_uid,
            add_into_active_row=_izom_propui_free_gl_add_into_active_row_enabled(params),
            params=params,
        )
        insert_after_layout_uid = (
            str(inserted_layouts[-1].get('uid', '') or '').strip()
            if inserted_layouts
            else prior_layout_active_uid
        )
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=insert_after_layout_uid or prior_layout_active_uid,
            sync_view_selection=False,
        )

    def _restore_duplicate_selection(self, params, duplicated_roots, active_uid, insertion_start):
        if len(duplicated_roots) == 1:
            _izom_propui_free_set_entry_selection_direct(params, active_uid, insertion_start + 1)
            return
        _izom_propui_free_set_entry_selection(
            params,
            duplicated_roots,
            active_uid=active_uid,
            anchor_uid=duplicated_roots[0] if duplicated_roots else active_uid,
            editor_context=self.editor_context,
            update_list_context=False,
        )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
