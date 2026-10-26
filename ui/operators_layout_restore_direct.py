# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_layout_live_core import (
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE,
    _izom_propui_free_json_dumps,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
    _izom_propui_free_sync_entry_layout_fields_simple_order_direct,
)
from ..core.cache_common import izom_propui_free_invalidate_params_cache_fields
from ..core.collection_sync import _izom_propui_free_collection_clear
from ..core.snapshot_layout_common import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS,
    _izom_propui_free_layout_row_snapshot_values,
)
from ..core.snapshot_layout_ensure import (
    _izom_propui_free_layout_view_entry_uid,
    _izom_propui_free_sync_entry_layout_fields,
)
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD
from .helper_selection_collections import _izom_propui_free_bump_collection_revision
from .operators_layout_view import _izom_propui_free_sync_layout_view_selection


def _izom_propui_free_add_layout_row_direct(row_collection, source, *, row_index):
    normalized = _izom_propui_free_layout_row_snapshot_values(source or {}, row_index=row_index)
    item = row_collection.add()
    guard_key = str(item.as_pointer())
    _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.add(guard_key)
    try:
        item.row_index = normalized['row_index']
        for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS:
            setattr(item, field_name, normalized[field_name])
    finally:
        _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.discard(guard_key)
    return item


def _izom_propui_free_restore_simple_single_row_layout_direct(
    params,
    layout_snapshots,
    *,
    active_layout_uid='',
    sync_view_selection=False,
):
    if params is None:
        return False
    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    row_collection = getattr(params, 'izom_propui_free_layout_rows', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if layout_collection is None or row_collection is None or view_collection is None:
        return False

    ordered_items = []
    ordered_entry_uids = []
    for expected_row, snap in enumerate(layout_snapshots or (), start=1):
        if not isinstance(snap, dict):
            return False
        try:
            row_index = max(1, int(snap.get('row_index', expected_row) or expected_row))
            column_index = max(1, int(snap.get('column_index', 1) or 1))
        except (TypeError, ValueError):
            return False
        if row_index != expected_row or column_index != 1:
            return False
        layout_uid = str(snap.get('uid', '') or '').strip()
        entry_uid = str(snap.get('entry_uid', '') or '').strip()
        if not layout_uid:
            return False
        ordered_items.append((
            layout_uid,
            entry_uid,
            expected_row,
            _izom_propui_free_layout_row_snapshot_values(snap, row_index=expected_row),
        ))
        ordered_entry_uids.append(entry_uid)

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        _izom_propui_free_collection_clear(layout_collection)
        _izom_propui_free_collection_clear(row_collection)
        for (
            layout_uid,
            entry_uid,
            row_index,
            row_snapshot,
        ) in ordered_items:
            _izom_propui_free_add_layout_row_direct(row_collection, row_snapshot, row_index=row_index)
            item = layout_collection.add()
            _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.add(layout_uid)
            try:
                item.uid = layout_uid
                item.entry_uid = entry_uid
                item.row_index = row_index
                item.column_index = 1
            finally:
                _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.discard(layout_uid)

        _izom_propui_free_collection_clear(view_collection)
        ui_order = 1
        for layout_uid, entry_uid, row_index, _row_snapshot in ordered_items:
            item = view_collection.add()
            item.uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
            item.kind = 'ENTRY_ITEM'
            item.layout_uid = layout_uid
            item.entry_uid = entry_uid
            item.parent_uid = ''
            item.row_index = row_index
            item.column_index = 1
            item.row_member_uids_json = '[]'
            item.ui_order = ui_order
            ui_order += 1
        if bool(sync_view_selection):
            _izom_propui_free_sync_layout_view_selection(
                params,
                preferred_active_uid=(
                    _izom_propui_free_layout_view_entry_uid(active_layout_uid)
                    if active_layout_uid else ''
                ),
            )
        if not _izom_propui_free_sync_entry_layout_fields_simple_order_direct(params, ordered_entry_uids):
            _izom_propui_free_sync_entry_layout_fields(params, [
                {
                    'uid': layout_uid,
                    'entry_uid': entry_uid,
                    'row_index': row_index,
                    'column_index': 1,
                }
                for layout_uid, entry_uid, row_index, _row_snapshot in ordered_items
            ])
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_rows')
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_view_items')
        _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
        izom_propui_free_invalidate_params_cache_fields(
            params,
            (
                'layout_snapshots',
                'layout_item_lookup',
                'visible_layout_rows',
                'generated_layout_state',
                'runtime_layout_entries',
            ),
        )
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    return True

def _izom_propui_free_restore_entry_order_layout_direct(
    params,
    entry_uids,
    *,
    active_entry_uid='',
    sync_view_selection=False,
    select_active=False,
):
    if params is None:
        return ''
    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    row_collection = getattr(params, 'izom_propui_free_layout_rows', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if layout_collection is None or row_collection is None or view_collection is None:
        return ''

    ordered_entry_uids = []
    for entry_uid in entry_uids or ():
        normalized_uid = str(entry_uid or '').strip()
        if normalized_uid:
            ordered_entry_uids.append(normalized_uid)
    if not ordered_entry_uids:
        return ''

    active_entry_uid = str(active_entry_uid or '').strip()
    active_index = 0
    if active_entry_uid:
        for entry_index, entry_uid in enumerate(ordered_entry_uids):
            if entry_uid == active_entry_uid:
                active_index = entry_index
                break
    ordered_layout_uids = [
        f"layout_{row_index}_{entry_uid}"
        for row_index, entry_uid in enumerate(ordered_entry_uids, start=1)
    ]
    active_layout_uid = ordered_layout_uids[active_index]
    active_view_uid = f"ENTRY_ITEM:{active_layout_uid}"

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        _izom_propui_free_collection_clear(layout_collection)
        _izom_propui_free_collection_clear(row_collection)
        _izom_propui_free_collection_clear(view_collection)

        guard_layout_uids = set(ordered_layout_uids)
        if guard_layout_uids:
            _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.update(guard_layout_uids)
        try:
            for row_index, (entry_uid, layout_uid) in enumerate(zip(ordered_entry_uids, ordered_layout_uids), start=1):
                _izom_propui_free_add_layout_row_direct(row_collection, {}, row_index=row_index)

                item = layout_collection.add()
                item.uid = layout_uid
                item.entry_uid = entry_uid
                item.row_index = row_index
                item.column_index = 1

                view_item = view_collection.add()
                view_item.uid = f"ENTRY_ITEM:{layout_uid}"
                view_item.kind = 'ENTRY_ITEM'
                view_item.layout_uid = layout_uid
                view_item.entry_uid = entry_uid
                view_item.parent_uid = ''
                view_item.row_index = row_index
                view_item.column_index = 1
                view_item.row_member_uids_json = '[]'
                view_item.ui_order = row_index
        finally:
            if guard_layout_uids:
                _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.difference_update(guard_layout_uids)

        if bool(select_active):
            params.izom_propui_free_layout_active_index = max(0, active_index)
            params.izom_propui_free_layout_active_uid = active_layout_uid
            params.izom_propui_free_layout_selected_uids_json = _izom_propui_free_json_dumps([active_layout_uid])
            params.izom_propui_free_layout_selection_anchor_uid = active_layout_uid
            params.izom_propui_free_layout_view_active_index = max(0, active_index)
            params.izom_propui_free_layout_view_active_uid = active_view_uid
            params.izom_propui_free_layout_view_selected_uids_json = _izom_propui_free_json_dumps([active_view_uid])
            params.izom_propui_free_layout_view_selection_anchor_uid = active_view_uid
        elif bool(sync_view_selection):
            _izom_propui_free_sync_layout_view_selection(
                params,
                preferred_active_uid=active_view_uid,
            )
        if not _izom_propui_free_sync_entry_layout_fields_simple_order_direct(
            params,
            ordered_entry_uids,
            trusted_order=True,
            assume_entry_collection_order=True,
        ):
            fallback_snapshots = [
                {
                    'uid': layout_uid,
                    'entry_uid': entry_uid,
                    'row_index': row_index,
                    'column_index': 1,
                }
                for row_index, (entry_uid, layout_uid) in enumerate(zip(ordered_entry_uids, ordered_layout_uids), start=1)
            ]
            _izom_propui_free_sync_entry_layout_fields(params, fallback_snapshots)
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_rows')
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_view_items')
        _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
        izom_propui_free_invalidate_params_cache_fields(
            params,
            (
                'layout_snapshots',
                'layout_item_lookup',
                'visible_layout_rows',
                'generated_layout_state',
                'runtime_layout_entries',
            ),
        )
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    return active_layout_uid


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
