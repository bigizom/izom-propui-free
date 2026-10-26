# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.types import Operator

from ..core.snapshot_layout_common import izom_propui_free_snapshot_layout_items
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from .confirmations import izom_propui_free_confirm_or_execute
from .helper_layout_view import (
    _izom_propui_free_active_layout_view_layout_uid,
    _izom_propui_free_set_layout_view_selection,
)
from .helper_selection_common import (
    _izom_propui_free_report_operator,
    _izom_propui_free_set_last_editor_context,
)
from .operators_layout_base import _izom_propui_free_entry_params
from .operators_layout_import import (
    _izom_propui_free_gl_safe_import_enabled,
    _izom_propui_free_import_entries_into_layout,
)
from .operators_layout_live_core import _izom_propui_free_set_simple_layout_view_selection_direct
from .operators_layout_restore_direct import (
    _izom_propui_free_restore_entry_order_layout_direct,
    _izom_propui_free_restore_simple_single_row_layout_direct,
)
from .operators_layout_restore_snapshots import _izom_propui_free_restore_layout_snapshots

class IZOM_PROPUI_FREE_OT_import_layout_entries(Operator):
    bl_idname = "wm.izom_propui_free_import_layout_entries"
    bl_label = "Import Generated Layout Entries"
    bl_description = "Import Entry List items into Generated Layout without changing the Entry List itself"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(params is not None)

    @classmethod
    def description(cls, _context, properties):
        return "Append Entry List items into Generated Layout. With Safe Import on, entries already present in Generated Layout are skipped"

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        entry_uids = [
            str(getattr(entry, 'uid', '') or '').strip()
            for entry in (getattr(params, 'izom_propui_free_entries', None) or ())
            if str(getattr(entry, 'uid', '') or '').strip()
        ]
        safe_import = _izom_propui_free_gl_safe_import_enabled(params)
        inserted_layout_uids = []
        can_fast_restore = False

        active_layout_uid = _izom_propui_free_active_layout_view_layout_uid(params, after=True)
        layout_snapshots = izom_propui_free_snapshot_layout_items(params)
        had_layout_before = bool(layout_snapshots)
        if not had_layout_before:
            active_result_uid = _izom_propui_free_restore_entry_order_layout_direct(
                params,
                entry_uids,
                active_entry_uid=entry_uids[-1] if entry_uids else '',
                sync_view_selection=False,
                select_active=True,
            )
            if active_result_uid:
                return {'FINISHED'}
        inserted_layout_uids = [
            str(inserted.get('uid', '') or '').strip()
            for inserted in _izom_propui_free_import_entries_into_layout(
                layout_snapshots,
                entry_uids,
                after_layout_uid=active_layout_uid,
                safe_import=safe_import,
                params=params,
            )
            if str(inserted.get('uid', '') or '').strip()
        ]
        if not inserted_layout_uids:
            _izom_propui_free_report_operator(self, 'INFO', 'No Entry List items were added to Generated Layout')
            return {'FINISHED'}
        can_fast_restore = not had_layout_before

        active_result_uid = inserted_layout_uids[-1] if inserted_layout_uids else ''
        fast_restored = bool(can_fast_restore) and _izom_propui_free_restore_simple_single_row_layout_direct(
            params,
            layout_snapshots,
            active_layout_uid=active_result_uid,
            sync_view_selection=False,
        )
        if not fast_restored:
            _izom_propui_free_restore_layout_snapshots(
                params,
                layout_snapshots,
                active_layout_uid=active_result_uid,
                layout_snapshots_are_ordered=True,
                sync_view_selection=False,
            )
        view_uid = _izom_propui_free_layout_view_entry_uid(active_result_uid) if active_result_uid else ''
        if not fast_restored or not _izom_propui_free_set_simple_layout_view_selection_direct(
            params,
            view_uid,
            active_result_uid,
        ):
            _izom_propui_free_set_layout_view_selection(
                params,
                [view_uid] if view_uid else [],
                active_uid=view_uid,
                anchor_uid=view_uid,
                update_list_context=False,
            )
        return {'FINISHED'}

class IZOM_PROPUI_FREE_OT_clear_layout_entries(Operator):
    bl_idname = "wm.izom_propui_free_clear_layout_entries"
    bl_label = "Clear Generated Layout"
    bl_description = "Clear Generated Layout without changing the Entry List"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(params and getattr(params, 'izom_propui_free_layout_items', None))

    def invoke(self, context, event):
        return izom_propui_free_confirm_or_execute(
            self, context, event, prop_name='izom_propui_free_confirmation_clear_generated_layout'
        )

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        _izom_propui_free_restore_layout_snapshots(
            params,
            [],
            active_layout_uid='',
            layout_snapshots_are_ordered=True,
            sync_view_selection=False,
        )
        _izom_propui_free_set_layout_view_selection(
            params,
            [],
            active_uid='',
            anchor_uid='',
            update_list_context=False,
        )
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401


__all__ = izom_propui_free_public_names(globals())
