# SPDX-License-Identifier: GPL-3.0-or-later


from .operators_layout_view import (
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE,
    _izom_propui_free_json_dumps,
    _izom_propui_free_layout_collapsed_row_uids,
    _izom_propui_free_layout_view_row_uid,
    _izom_propui_free_prune_layout_collapsed_row_uids,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
    _izom_propui_free_uid_list_from_json,
    izom_propui_free_log_recovered,
)
from ..core.cache_common import izom_propui_free_invalidate_params_cache_fields
from ..core.snapshot_layout_common import IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD
from .helper_layout_view import _izom_propui_free_set_layout_view_selection
from .helper_selection_collections import _izom_propui_free_bump_collection_revision


_IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_layout_item_position(rows, item_uid):
    target_uid = str(item_uid or '').strip()
    if not target_uid:
        return -1, -1
    for row_index, row in enumerate(rows or []):
        for column_index, uid in enumerate(row or []):
            if str(uid or '').strip() == target_uid:
                return row_index, column_index
    return -1, -1

def _izom_propui_free_collection_item_and_index_by_uid(collection, uid):
    target_uid = str(uid or '').strip()
    if not target_uid:
        return None, -1
    for index, item in enumerate(collection or ()):
        if str(getattr(item, 'uid', '') or '').strip() == target_uid:
            return item, index
    return None, -1

def _izom_propui_free_swap_collection_items(collection, index_a, index_b):
    if collection is None:
        return
    try:
        source_index = int(index_a)
        target_index = int(index_b)
    except (TypeError, ValueError):
        return
    if source_index == target_index:
        return
    try:
        collection.move(source_index, target_index)
    except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )

def _izom_propui_free_row_item_and_index(row_collection, row_index):
    try:
        target_row = max(1, int(row_index or 1))
    except (TypeError, ValueError):
        target_row = 1
    for index, item in enumerate(row_collection or ()):
        try:
            item_row = max(1, int(getattr(item, 'row_index', 1) or 1))
        except (TypeError, ValueError):
            item_row = 1
        if item_row == target_row:
            return item, index
    return None, -1

def _izom_propui_free_sort_layout_row_collection(row_collection):
    if row_collection is None or not hasattr(row_collection, 'move'):
        return
    row_indices = []
    for item in row_collection:
        try:
            row_indices.append(max(1, int(getattr(item, 'row_index', 1) or 1)))
        except (TypeError, ValueError):
            row_indices.append(1)
    for target_index, row_index in enumerate(sorted(row_indices)):
        current_index = -1
        for index in range(target_index, len(row_collection)):
            try:
                candidate_row = max(1, int(getattr(row_collection[index], 'row_index', 1) or 1))
            except (TypeError, ValueError):
                candidate_row = 1
            if candidate_row == row_index:
                current_index = index
                break
        if current_index >= 0 and current_index != target_index:
            row_collection.move(current_index, target_index)

def _izom_propui_free_layout_row_fields_from_item(item):
    return {
        field_name: getattr(item, field_name)
        for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS
        if hasattr(item, field_name)
    }

def _izom_propui_free_apply_layout_row_fields_to_item(item, row_fields):
    if item is None:
        return
    for field_name, value in (row_fields or {}).items():
        if hasattr(item, field_name):
            try:
                setattr(item, field_name, value)
            except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )

def _izom_propui_free_sorted_layout_items_for_rows(layout_collection, row_indices):
    requested_rows = set()
    for row_index in row_indices or ():
        try:
            requested_rows.add(max(1, int(row_index or 1)))
        except (TypeError, ValueError):
            requested_rows.add(1)
    if not requested_rows:
        return {}

    items_by_row = {row_index: [] for row_index in requested_rows}
    for item in layout_collection or ():
        try:
            item_row = max(1, int(getattr(item, 'row_index', 1) or 1))
        except (TypeError, ValueError):
            item_row = 1
        if item_row not in items_by_row:
            continue
        items_by_row[item_row].append(item)
    for row_items in items_by_row.values():
        row_items.sort(key=lambda item: int(getattr(item, 'column_index', 1) or 1))
    return items_by_row

def _izom_propui_free_layout_uids_from_items(items):
    return [
        str(getattr(item, 'uid', '') or '').strip()
        for item in (items or ())
        if str(getattr(item, 'uid', '') or '').strip()
    ]

def _izom_propui_free_view_row_header_by_members(view_collection, member_uids):
    header_uid = _izom_propui_free_layout_view_row_uid(member_uids)
    return _izom_propui_free_collection_item_and_index_by_uid(view_collection, header_uid)

def _izom_propui_free_renumber_layout_view_order(view_collection):
    for ui_order, item in enumerate(view_collection or (), start=1):
        try:
            item.ui_order = ui_order
        except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )

def _izom_propui_free_finish_direct_layout_row_edit(
    params,
    layout_collection,
    *,
    selected_view_uid='',
):
    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_rows')
    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_view_items')
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
    if _izom_propui_free_layout_collapsed_row_uids(params):
        valid_row_uids = [
            str(getattr(item, 'uid', '') or '').strip()
            for item in getattr(params, 'izom_propui_free_layout_view_items', None) or ()
            if str(getattr(item, 'kind', '') or '').strip() == 'ROW_HEADER'
            and str(getattr(item, 'uid', '') or '').strip()
        ]
        _izom_propui_free_prune_layout_collapsed_row_uids(params, valid_row_uids)
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
    if selected_view_uid:
        if not _izom_propui_free_set_simple_layout_view_selection_direct(params, selected_view_uid):
            _izom_propui_free_set_layout_view_selection(
                params,
                [selected_view_uid],
                active_uid=selected_view_uid,
                anchor_uid=selected_view_uid,
                update_list_context=False,
            )

def _izom_propui_free_set_simple_layout_view_selection_direct(params, view_uid, layout_uid=''):
    if params is None:
        return False
    view_uid = str(view_uid or '').strip()
    layout_uid = str(layout_uid or '').strip()
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    if view_collection is None or layout_collection is None:
        return False

    view_index = -1
    if view_uid:
        for index, item in enumerate(view_collection):
            if str(getattr(item, 'uid', '') or '').strip() == view_uid:
                view_index = index
                if not layout_uid:
                    layout_uid = str(getattr(item, 'layout_uid', '') or '').strip()
                    if not layout_uid:
                        row_member_uids = _izom_propui_free_uid_list_from_json(
                            getattr(item, 'row_member_uids_json', '[]')
                        )
                        layout_uid = row_member_uids[0] if row_member_uids else ''
                break
    layout_index = -1
    if not layout_uid and len(layout_collection):
        layout_uid = str(getattr(layout_collection[0], 'uid', '') or '').strip()
    if layout_uid:
        for index, item in enumerate(layout_collection):
            if str(getattr(item, 'uid', '') or '').strip() == layout_uid:
                layout_index = index
                break
    if view_uid and view_index < 0:
        return False
    if layout_uid and layout_index < 0:
        return False

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        params.izom_propui_free_layout_active_index = max(0, layout_index)
        params.izom_propui_free_layout_active_uid = layout_uid
        params.izom_propui_free_layout_selected_uids_json = _izom_propui_free_json_dumps([layout_uid] if layout_uid else [])
        params.izom_propui_free_layout_selection_anchor_uid = layout_uid
        params.izom_propui_free_layout_view_active_index = max(0, view_index)
        params.izom_propui_free_layout_view_active_uid = view_uid
        params.izom_propui_free_layout_view_selected_uids_json = _izom_propui_free_json_dumps([view_uid] if view_uid else [])
        params.izom_propui_free_layout_view_selection_anchor_uid = view_uid
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    return True

def _izom_propui_free_sync_entry_layout_fields_simple_order_direct(
    params,
    ordered_entry_uids,
    *,
    trusted_order=False,
    assume_entry_collection_order=False,
):
    entries = getattr(params, 'izom_propui_free_entries', None)
    if entries is None:
        return False
    try:
        if len(entries) != len(ordered_entry_uids or ()):
            return False
    except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS:
        return False

    if bool(trusted_order):
        guard_keys = {
            str(entry_uid or '').strip()
            for entry_uid in (ordered_entry_uids or ())
            if str(entry_uid or '').strip()
        }
        if guard_keys:
            _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.update(guard_keys)
        try:
            if bool(assume_entry_collection_order):
                for index, entry in enumerate(entries, start=1):
                    try:
                        if int(getattr(entry, 'display_order', 1) or 1) != index:
                            entry.display_order = index
                        if int(getattr(entry, 'row_slot', 1) or 1) != 1:
                            entry.row_slot = 1
                    except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS:
                        return False
            else:
                for index, entry_uid in enumerate(ordered_entry_uids or (), start=1):
                    entry = entries[index - 1]
                    current_entry_uid = str(getattr(entry, 'uid', '') or '').strip()
                    if not current_entry_uid or current_entry_uid != str(entry_uid or '').strip():
                        return False
                    try:
                        if int(getattr(entry, 'display_order', 1) or 1) != index:
                            entry.display_order = index
                        if int(getattr(entry, 'row_slot', 1) or 1) != 1:
                            entry.row_slot = 1
                    except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS:
                        return False
        finally:
            if guard_keys:
                _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.difference_update(guard_keys)
        return True

    pending_updates = []
    for index, entry_uid in enumerate(ordered_entry_uids or (), start=1):
        entry = entries[index - 1]
        current_entry_uid = str(getattr(entry, 'uid', '') or '').strip()
        if not current_entry_uid or current_entry_uid != str(entry_uid or '').strip():
            return False
        try:
            current_order = int(getattr(entry, 'display_order', 1) or 1)
            current_slot = int(getattr(entry, 'row_slot', 1) or 1)
        except _IZOM_PROPUI_FREE_LAYOUT_LIVE_ACCESS_ERRORS:
            return False
        update_order = current_order != index
        update_slot = current_slot != 1
        if update_order or update_slot:
            pending_updates.append((entry, index, current_entry_uid, update_order, update_slot))

    guard_keys = {
        uid
        for _entry, _index, uid, _update_order, _update_slot in pending_updates
        if uid
    }
    if guard_keys:
        _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.update(guard_keys)
    try:
        for entry, index, _uid, update_order, update_slot in pending_updates:
            if update_order:
                entry.display_order = index
            if update_slot:
                entry.row_slot = 1
    finally:
        if guard_keys:
            _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.difference_update(guard_keys)
    return True

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
