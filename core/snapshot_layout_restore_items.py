# SPDX-License-Identifier: GPL-3.0-or-later

from types import SimpleNamespace

from .collection_sync import _izom_propui_free_collection_clear
from .snapshot_layout_common import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS,
    _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS,
    _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS,
    _izom_propui_free_apply_layout_rows_to_snapshots,
    _izom_propui_free_layout_row_snapshot_values,
    _izom_propui_free_layout_rows_from_layout_snapshots,
    _izom_propui_free_restore_layout_selection_state,
    _izom_propui_free_snapshot_layout_row,
    _izom_propui_free_suspended_list_context,
    izom_propui_free_snapshot_layout_rows,
)


def _izom_propui_free_layout_view_entry_uid(layout_uid):
    return f"ENTRY_ITEM:{str(layout_uid or '').strip()}"


def _izom_propui_free_apply_layout_snapshot_item(item, snap, *, ui_helpers=None):
    item_uid = str(snap['uid'] or '').strip()
    if ui_helpers is not None and item_uid:
        ui_helpers._IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.add(item_uid)
    try:
        item.uid = item_uid
        item.entry_uid = str(snap['entry_uid'] or '').strip()
        item.row_index = max(1, int(snap['row_index'] or 1))
        item.column_index = max(1, int(snap['column_index'] or 1))
    finally:
        if ui_helpers is not None and item_uid:
            ui_helpers._IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.discard(item_uid)


def _izom_propui_free_apply_layout_row_snapshot_item(item, snap):
    normalized = _izom_propui_free_layout_row_snapshot_values(snap)
    item.row_index = normalized['row_index']
    for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS:
        setattr(item, field_name, normalized[field_name])


def _izom_propui_free_restore_layout_rows(params, row_snapshots, *, return_snapshots=True, rows_are_normalized=False):
    collection = getattr(params, 'izom_propui_free_layout_rows', None)
    if collection is None:
        return []

    normalized_snapshots = []
    for snap in row_snapshots or []:
        normalized_snapshots.append(
            dict(snap)
            if bool(rows_are_normalized)
            else _izom_propui_free_layout_row_snapshot_values(snap)
        )

    with _izom_propui_free_suspended_list_context(params):
        _izom_propui_free_collection_clear(collection)
        for snap in normalized_snapshots:
            if hasattr(collection, 'add') and not isinstance(collection, list):
                item = collection.add()
            else:
                item = SimpleNamespace()
                collection.append(item)
            _izom_propui_free_apply_layout_row_snapshot_item(item, snap)

    if not return_snapshots:
        return []
    return [_izom_propui_free_snapshot_layout_row(item) for item in collection]


def _izom_propui_free_restore_layout_items_full(
    params,
    layout_snapshots,
    active_uid=None,
    rebuild_view=True,
    return_snapshots=True,
):
    collection = getattr(params, 'izom_propui_free_layout_items', None)
    if collection is None:
        return []

    target_uid = str(active_uid or getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
    active_index = 0
    resolved = [] if return_snapshots else None

    with _izom_propui_free_suspended_list_context(params) as ui_helpers:
        _izom_propui_free_collection_clear(collection)
        for index, snap in enumerate(layout_snapshots or []):
            if hasattr(collection, 'add') and not isinstance(collection, list):
                item = collection.add()
            else:
                item = SimpleNamespace()
                collection.append(item)
            _izom_propui_free_apply_layout_snapshot_item(item, snap, ui_helpers=ui_helpers)
            if target_uid and item.uid == target_uid:
                active_index = index
            if resolved is not None:
                resolved.append({
                    'uid': item.uid,
                    'entry_uid': item.entry_uid,
                    'row_index': item.row_index,
                    'column_index': item.column_index,
                })

        _izom_propui_free_restore_layout_selection_state(params, collection, active_index)

        if bool(rebuild_view):
            try:
                from ..ui.operators_layout_view import _izom_propui_free_rebuild_layout_view_items

                _izom_propui_free_rebuild_layout_view_items(
                    params,
                    preferred_active_uid=_izom_propui_free_layout_view_entry_uid(target_uid) if target_uid else '',
                    layout_snapshots=layout_snapshots,
                    layout_snapshots_are_ordered=True,
                )
            except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS:
                pass

    if not return_snapshots:
        return []
    return _izom_propui_free_apply_layout_rows_to_snapshots(resolved, izom_propui_free_snapshot_layout_rows(params))


def _izom_propui_free_restore_layout_items(
    params,
    layout_snapshots,
    active_uid=None,
    row_snapshots=None,
    rebuild_view=True,
    return_snapshots=True,
    assume_canonical=False,
):
    if assume_canonical and row_snapshots is None:
        joined_snapshots = list(layout_snapshots or [])
    else:
        canonical_rows = _izom_propui_free_layout_rows_from_layout_snapshots(layout_snapshots, row_snapshots=row_snapshots)
        joined_snapshots = _izom_propui_free_apply_layout_rows_to_snapshots(layout_snapshots, canonical_rows)
    canonical_rows = _izom_propui_free_layout_rows_from_layout_snapshots(joined_snapshots)
    _izom_propui_free_restore_layout_rows(params, canonical_rows, return_snapshots=False, rows_are_normalized=True)
    return _izom_propui_free_restore_layout_items_full(
        params,
        joined_snapshots,
        active_uid=active_uid,
        rebuild_view=bool(rebuild_view),
        return_snapshots=bool(return_snapshots),
    )


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
