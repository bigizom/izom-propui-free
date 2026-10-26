# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_value_labels_common import (
    IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS,
    _izom_propui_free_active_value_label_index_direct,
    _izom_propui_free_finalize_value_label_thresholds,
    _izom_propui_free_finish_value_label_collection_mutation,
    _izom_propui_free_focus_value_label_editor,
    _izom_propui_free_new_uid,
    _izom_propui_free_restore_value_label_item,
    _izom_propui_free_selected_value_label_indexes_direct,
    _izom_propui_free_selected_value_label_uids,
    _izom_propui_free_snapshot_value_label_item,
    _izom_propui_free_value_label_collection_name,
    _izom_propui_free_value_label_operator_entry,
    _izom_propui_free_value_label_target_info,
    _izom_propui_free_value_label_target_mode_label,
    izom_propui_free_context_params,
    izom_propui_free_log_recovered,
)
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator
from copy import deepcopy
from types import SimpleNamespace
from ..core.cache_value_labels import izom_propui_free_remember_value_label_owner



class IZOM_PROPUI_FREE_OT_duplicate_value_label(Operator):
    bl_idname = "wm.izom_propui_free_duplicate_value_label"
    bl_label = "Duplicate Dynamic Labels"
    bl_description = "Duplicate the selected dynamic-label rows"
    bl_options = {'UNDO', 'INTERNAL'}

    target_mode: EnumProperty(
        name="Target Mode",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS,
        default='SELF',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params is not None and len(getattr(params, 'izom_propui_free_entries', []) or []) > 0)

    @classmethod
    def description(cls, _context, properties):
        return f"Duplicate the selected row in {_izom_propui_free_value_label_target_mode_label(getattr(properties, 'target_mode', 'SELF'))}"

    def execute(self, context):
        ctx = self._duplicate_context(context)
        if ctx is None:
            return {'CANCELLED'}
        selected_items = self._selected_value_label_snapshots(ctx)
        if not selected_items:
            return {'CANCELLED'}
        self._restore_duplicate_snapshots(ctx, selected_items)
        _izom_propui_free_finalize_value_label_thresholds(
            ctx.collection,
            ctx.entry,
            ctx.active_owner,
            ctx.collection_name,
            ctx.info,
        )
        self._finish_duplicate_collection_mutation(ctx, ctx.duplicated_uids)
        return {'FINISHED'}

    def _duplicate_context(self, context):
        entry = _izom_propui_free_value_label_operator_entry(context, getattr(self, 'entry_uid', ''))
        info = _izom_propui_free_value_label_target_info(entry, context, self.target_mode)
        if not info or len(info['collection']) == 0:
            return None
        collection = info['collection']
        active_owner = info.get('active_owner', entry)
        collection_name = _izom_propui_free_value_label_collection_name(self.target_mode)
        _izom_propui_free_focus_value_label_editor(info, self.target_mode)
        selected_uids = _izom_propui_free_selected_value_label_uids(active_owner, collection_name)
        if not selected_uids:
            return None
        selected_indexes = _izom_propui_free_selected_value_label_indexes_direct(
            active_owner,
            collection_name,
            collection,
            selected_uids,
        )
        return SimpleNamespace(
            entry=entry,
            info=info,
            params=info.get('params'),
            collection=collection,
            active_owner=active_owner,
            collection_name=collection_name,
            selected_uids=selected_uids,
            selected_indexes=selected_indexes,
            duplicated_uids=[],
        )

    def _selected_value_label_snapshots(self, ctx):
        return [
            _izom_propui_free_snapshot_value_label_item(ctx.collection[index])
            for index in ctx.selected_indexes
            if 0 <= index < len(ctx.collection)
        ]

    def _restore_duplicate_snapshots(self, ctx, selected_items):
        insert_index = max(ctx.selected_indexes) + 1
        for snap in selected_items:
            new_snap = self._new_duplicate_snapshot(snap)
            _izom_propui_free_restore_value_label_item(ctx.collection, new_snap, params=ctx.params)
            ctx.collection.move(len(ctx.collection) - 1, insert_index)
            insert_index += 1
            new_uid = str(new_snap.get('uid', '') or '').strip()
            candidate = self._candidate_at_index(ctx.collection, insert_index - 1)
            if candidate is not None:
                izom_propui_free_remember_value_label_owner(
                    ctx.params,
                    candidate,
                    ctx.entry,
                    ctx.active_owner,
                    ctx.collection_name,
                    insert_index - 1,
                )
            ctx.duplicated_uids.append(new_uid)

    def _new_duplicate_snapshot(self, snap):
        new_snap = deepcopy(snap)
        new_snap['uid'] = _izom_propui_free_new_uid()
        return new_snap

    def _candidate_at_index(self, collection, index):
        try:
            return collection[index]
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            return None

    def _finish_duplicate_collection_mutation(self, ctx, selected_uids):
        active_uid = selected_uids[-1] if selected_uids else ''
        active_index = _izom_propui_free_active_value_label_index_direct(
            ctx.active_owner,
            ctx.collection_name,
            ctx.collection,
            [active_uid],
        )
        _izom_propui_free_finish_value_label_collection_mutation(
            ctx.active_owner,
            ctx.collection_name,
            ctx.collection,
            active_uid,
            active_index if active_index >= 0 else 0,
            selected_uids=selected_uids,
            anchor_uid=selected_uids[0] if selected_uids else active_uid,
            params=ctx.params,
        )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
