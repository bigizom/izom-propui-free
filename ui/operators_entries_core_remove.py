# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from bpy.props import EnumProperty
from bpy.types import Operator

from .operators_entries_core_common import (
    _izom_propui_free_remove_active_leaf_entry_direct,
    _izom_propui_free_remove_layout_item_for_entry_direct,
    _izom_propui_free_remove_layout_snapshots_by_entry_uids,
    _izom_propui_free_restore_layout_snapshots,
    _izom_propui_free_set_entry_selection_direct,
    _izom_propui_free_set_layout_view_selection,
    _izom_propui_free_uid_list_from_json,
    izom_propui_free_snapshot_layout_items,
)
from ..core.cache_state import izom_propui_free_cached_state_bundle
from ..core.context import izom_propui_free_context_params
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from ..core.snapshot_tree import _izom_propui_free_subtree_end
from .confirmations import izom_propui_free_confirmation_value
from .helper_layout_lookup import _izom_propui_free_layout_item_uid_order
from .helper_layout_view import (
    _izom_propui_free_active_layout_view_item,
    _izom_propui_free_active_layout_view_layout_uid,
)
from .helper_selection_common import _izom_propui_free_set_last_editor_context
from .operators_entries_shared_common import (
    _izom_propui_free_entry_operator_description,
    _izom_propui_free_selected_root_uids,
)
from .operators_entries_shared_order import (
    _izom_propui_free_active_entry_uid_direct,
    _izom_propui_free_entry_order_state_direct,
    _izom_propui_free_selected_entry_uids_direct,
)
from .operators_entries_shared_structure import _izom_propui_free_remove_entry_uids_direct
from .operators_layout_import import _izom_propui_free_next_layout_focus_uid
from .operators_layout_mutation import (
    _izom_propui_free_remove_layout_snapshots_by_uids,
    _izom_propui_free_ungroup_layout_row,
)



class IZOM_PROPUI_FREE_OT_remove_entry(Operator):
    bl_idname = "wm.izom_propui_free_remove_entry"
    bl_label = "Remove izom PropUI Entry"
    bl_description = "Remove the selected izom PropUI item"
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
    delete_mode: EnumProperty(
        name="Delete Mode",
        items=[
            ('DELETE', 'Delete', 'Delete the parent only and promote its children one level up'),
            ('DELETE_HIERARCHY', 'Delete Hierarchy', 'Delete the parent and its child hierarchy'),
        ],
        default='DELETE',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        if params is None:
            return False
        return (
            len(getattr(params, 'izom_propui_free_entries', []) or []) > 0
        )

    @classmethod
    def description(cls, _context, properties):
        return _izom_propui_free_entry_operator_description(
            'remove',
            editor_context=getattr(properties, 'editor_context', 'HIERARCHY'),
        )

    def _hierarchy_delete_prompt_required(self, params):
        if params is None:
            return False
        snapshots, index_by_uid, tree_state, _order = _izom_propui_free_entry_order_state_direct(params)
        if not snapshots:
            return False
        selected = set(_izom_propui_free_selected_entry_uids_direct(params, snapshots, index_by_uid))
        roots = _izom_propui_free_selected_root_uids(snapshots, selected, index_by_uid=index_by_uid)
        if not roots:
            active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
            roots = [active_uid] if active_uid else []
        children_by_uid = tree_state.get('children_by_uid', {}) or {}
        return any(str(uid or '').strip() in children_by_uid for uid in roots)

    def invoke(self, context, event):
        if str(self.editor_context or 'HIERARCHY').strip().upper() != 'HIERARCHY':
            return self.execute(context)

        params = izom_propui_free_context_params(context)
        if params is None:
            return {'CANCELLED'}

        if bool(getattr(event, 'shift', False)):
            self.delete_mode = 'DELETE_HIERARCHY'
            return self.execute(context)

        self.delete_mode = 'DELETE'
        if self._hierarchy_delete_prompt_required(params):
            behavior = izom_propui_free_confirmation_value(
                params,
                'izom_propui_free_confirmation_parent_delete',
                default='ASK',
            )
            if behavior in {'DELETE', 'DELETE_HIERARCHY'}:
                self.delete_mode = behavior
                return self.execute(context)
            return context.window_manager.invoke_props_dialog(self, width=320)
        return self.execute(context)

    def draw(self, _context):
        if str(self.editor_context or 'HIERARCHY').strip().upper() != 'HIERARCHY':
            return
        layout = self.layout
        layout.label(text="Selection includes a parent. Choose how to delete it.", icon='QUESTION')
        layout.prop(self, 'delete_mode', expand=True)

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        area = getattr(context, 'area', None)
        _izom_propui_free_set_last_editor_context(params, self.editor_context)
        if self.editor_context == 'LAYOUT':
            return self._execute_layout_remove(params, area)
        return self._execute_hierarchy_remove(params, area)

    def _execute_layout_remove(self, params, area):
        layout_snapshots = [
            dict(snap)
            for snap in (izom_propui_free_cached_state_bundle(params).get('layout_snapshots') or ())
        ]
        active_view_item = _izom_propui_free_active_layout_view_item(params, strict_uid=True)
        if active_view_item is None:
            return {'CANCELLED'}

        active_kind = str(getattr(active_view_item, 'kind', '') or '').strip()
        if active_kind == 'ROW_HEADER':
            return self._remove_layout_row_header(params, area, layout_snapshots, active_view_item)
        return self._remove_layout_entry(params, area, layout_snapshots, active_view_item)

    def _remove_layout_row_header(self, params, area, layout_snapshots, active_view_item):
        row_number = int(getattr(active_view_item, 'row_index', 1) or 1)
        next_row_member_uids = _izom_propui_free_uid_list_from_json(
            getattr(active_view_item, 'row_member_uids_json', '[]')
        )
        if not _izom_propui_free_ungroup_layout_row(layout_snapshots, row_number, params=params):
            return {'CANCELLED'}
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=_izom_propui_free_active_layout_view_layout_uid(params),
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        next_view_uid = _izom_propui_free_layout_view_entry_uid(next_row_member_uids[0]) if next_row_member_uids else ''
        _izom_propui_free_set_layout_view_selection(
            params,
            [next_view_uid] if next_view_uid else [],
            active_uid=next_view_uid,
            anchor_uid=next_view_uid,
            update_list_context=False,
        )
        self._tag_area_redraw(area)
        return {'FINISHED'}

    def _remove_layout_entry(self, params, area, layout_snapshots, active_view_item):
        active_layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
        if not active_layout_uid:
            return {'CANCELLED'}
        ordered_before = _izom_propui_free_layout_item_uid_order(params, visible_only=True)
        if not _izom_propui_free_remove_layout_snapshots_by_uids(layout_snapshots, {active_layout_uid}, params=params):
            return {'CANCELLED'}
        next_layout_uid = _izom_propui_free_next_layout_focus_uid(ordered_before, {active_layout_uid}, active_layout_uid)
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=next_layout_uid,
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
        self._tag_area_redraw(area)
        return {'FINISHED'}

    def _execute_hierarchy_remove(self, params, area):
        prior_layout_active_uid = str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
        delete_hierarchy = str(getattr(self, 'delete_mode', 'DELETE') or 'DELETE').strip().upper() == 'DELETE_HIERARCHY'
        if not delete_hierarchy and _izom_propui_free_remove_active_leaf_entry_direct(params, prior_layout_active_uid):
            self._tag_area_redraw(area)
            return {'FINISHED'}

        snapshots, index_by_uid, tree_state, order_before = _izom_propui_free_entry_order_state_direct(params)
        if not snapshots:
            return {'CANCELLED'}
        roots = self._remove_roots(params, snapshots, index_by_uid)
        if not roots:
            return {'CANCELLED'}

        active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
        ordered_roots = [uid for uid in order_before if uid in roots]
        removed_uids, parent_updates = self._entry_removal_plan(
            snapshots,
            index_by_uid,
            tree_state,
            ordered_roots or roots,
            delete_hierarchy,
        )
        if not _izom_propui_free_remove_entry_uids_direct(params, removed_uids, parent_updates=parent_updates):
            return {'CANCELLED'}

        self._remove_deleted_entries_from_layout(params, removed_uids, prior_layout_active_uid)
        self._restore_remove_selection(
            params,
            snapshots,
            index_by_uid,
            order_before,
            ordered_roots,
            removed_uids,
            active_uid,
        )
        self._tag_area_redraw(area)
        return {'FINISHED'}

    def _remove_roots(self, params, snapshots, index_by_uid):
        selected = set(_izom_propui_free_selected_entry_uids_direct(params, snapshots, index_by_uid))
        roots = _izom_propui_free_selected_root_uids(snapshots, selected, index_by_uid=index_by_uid)
        if roots:
            return roots
        active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
        return [active_uid] if active_uid else []

    def _entry_removal_plan(self, snapshots, index_by_uid, tree_state, ordered_roots, delete_hierarchy):
        children_by_uid = tree_state.get('children_by_uid', {}) or {}
        removed_uids = set()
        parent_updates = {}
        for target_uid in reversed(ordered_roots):
            target_uid = str(target_uid or '').strip()
            if not target_uid:
                continue
            if delete_hierarchy:
                self._mark_subtree_removed(
                    snapshots,
                    index_by_uid,
                    tree_state,
                    removed_uids,
                    target_uid,
                )
            else:
                self._mark_single_entry_removed(
                    snapshots,
                    index_by_uid,
                    children_by_uid,
                    removed_uids,
                    parent_updates,
                    target_uid,
                )
        return removed_uids, parent_updates

    def _mark_subtree_removed(self, snapshots, index_by_uid, tree_state, removed_uids, target_uid):
        index = index_by_uid.get(target_uid)
        if index is None:
            return
        block_end = _izom_propui_free_subtree_end(snapshots, index, state=tree_state)
        removed_uids.update(
            str(snap.get('uid', '') or '').strip()
            for snap in snapshots[index:block_end]
            if str(snap.get('uid', '') or '').strip()
        )

    def _mark_single_entry_removed(self, snapshots, index_by_uid, children_by_uid, removed_uids, parent_updates, target_uid):
        target_index = index_by_uid.get(target_uid)
        if target_index is None:
            return
        parent_uid = str(snapshots[target_index].get('parent_uid', '') or '').strip()
        for child_uid in tuple((children_by_uid or {}).get(target_uid, ()) or ()):
            child_uid = str(child_uid or '').strip()
            if child_uid and child_uid not in removed_uids:
                parent_updates[child_uid] = parent_uid
        removed_uids.add(target_uid)

    def _remove_deleted_entries_from_layout(self, params, removed_uids, prior_layout_active_uid):
        layout_changed = _izom_propui_free_remove_layout_item_for_entry_direct(params, removed_uids)
        if layout_changed:
            self._clear_missing_active_layout_selection(params, prior_layout_active_uid)
            return

        layout_snapshots = [dict(snap) for snap in izom_propui_free_snapshot_layout_items(params)]
        layout_changed = _izom_propui_free_remove_layout_snapshots_by_entry_uids(
            layout_snapshots,
            removed_uids,
            params=params,
        )
        if not layout_changed:
            return
        active_layout_uid = prior_layout_active_uid
        if active_layout_uid and not any(
            str(snap.get('uid', '') or '').strip() == active_layout_uid
            for snap in layout_snapshots
        ):
            active_layout_uid = ''
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=active_layout_uid,
            sync_view_selection=False,
        )

    def _clear_missing_active_layout_selection(self, params, prior_layout_active_uid):
        active_layout_uid = prior_layout_active_uid
        if active_layout_uid:
            layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
            if not any(
                str(getattr(item, 'uid', '') or '').strip() == active_layout_uid
                for item in (layout_collection or ())
            ):
                active_layout_uid = ''
        if active_layout_uid:
            return
        _izom_propui_free_set_layout_view_selection(
            params,
            [],
            active_uid='',
            anchor_uid='',
            update_list_context=False,
        )

    def _restore_remove_selection(self, params, snapshots, index_by_uid, order_before, ordered_roots, removed_uids, active_uid):
        focus_uid = active_uid if active_uid in order_before else ''
        if not focus_uid and ordered_roots:
            focus_uid = ordered_roots[0]
        next_uid = _izom_propui_free_next_layout_focus_uid(order_before, removed_uids, focus_uid)
        if next_uid:
            removed_indices = sorted(
                index_by_uid[uid]
                for uid in removed_uids
                if uid in index_by_uid
            )
            old_next_index = index_by_uid.get(next_uid, 0)
            next_index = old_next_index - sum(1 for index in removed_indices if index < old_next_index)
        else:
            next_index = 0
        _izom_propui_free_set_entry_selection_direct(params, next_uid, next_index)

    def _tag_area_redraw(self, area):
        if area is None:
            return
        try:
            area.tag_redraw()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
