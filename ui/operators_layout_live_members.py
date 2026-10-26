# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_layout_live_core import (
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE,
    _izom_propui_free_collection_item_and_index_by_uid,
    _izom_propui_free_json_dumps,
    _izom_propui_free_layout_view_row_uid,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_set_simple_layout_view_selection_direct,
    _izom_propui_free_suspend_list_context_updates,
    _izom_propui_free_swap_collection_items,
    izom_propui_free_log_recovered,
)
from ..core.cache_common import izom_propui_free_invalidate_params_cache_fields
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from .helper_layout_rows import _izom_propui_free_layout_view_row_member_uids
from .helper_layout_view import _izom_propui_free_layout_view_item_by_uid
from .helper_selection_collections import _izom_propui_free_bump_collection_revision



def _izom_propui_free_move_layout_view_row_member_direct(params, view_item, direction):
    if params is None or view_item is None:
        return False, ''
    if str(getattr(view_item, 'kind', '') or '').strip() != 'ENTRY_ITEM':
        return False, ''

    layout_uid = str(getattr(view_item, 'layout_uid', '') or '').strip()
    row_header_uid = str(getattr(view_item, 'parent_uid', '') or '').strip()
    if not layout_uid or not row_header_uid.startswith('ROW_HEADER:'):
        return False, ''

    row_header = _izom_propui_free_layout_view_item_by_uid(params, row_header_uid)
    member_uids = _izom_propui_free_layout_view_row_member_uids(row_header)
    if len(member_uids) <= 1 or layout_uid not in member_uids:
        return False, ''

    direction = str(direction or 'UP').strip().upper()
    member_index = member_uids.index(layout_uid)
    if direction == 'UP':
        if member_index <= 0:
            return False, ''
        target_member_index = member_index - 1
    elif direction == 'DOWN':
        if member_index >= len(member_uids) - 1:
            return False, ''
        target_member_index = member_index + 1
    else:
        return False, ''

    target_layout_uid = member_uids[target_member_index]
    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    layout_item, layout_index = _izom_propui_free_collection_item_and_index_by_uid(layout_collection, layout_uid)
    target_layout_item, target_layout_index = _izom_propui_free_collection_item_and_index_by_uid(layout_collection, target_layout_uid)
    view_uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
    target_view_uid = _izom_propui_free_layout_view_entry_uid(target_layout_uid)
    active_view_item, view_index = _izom_propui_free_collection_item_and_index_by_uid(view_collection, view_uid)
    target_view_item, target_view_index = _izom_propui_free_collection_item_and_index_by_uid(view_collection, target_view_uid)
    if (
        layout_item is None
        or target_layout_item is None
        or active_view_item is None
        or target_view_item is None
    ):
        return False, ''

    next_member_uids = list(member_uids)
    next_member_uids[member_index], next_member_uids[target_member_index] = (
        next_member_uids[target_member_index],
        next_member_uids[member_index],
    )
    next_header_uid = _izom_propui_free_layout_view_row_uid(next_member_uids)

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        layout_item.column_index, target_layout_item.column_index = (
            int(getattr(target_layout_item, 'column_index', target_member_index + 1) or (target_member_index + 1)),
            int(getattr(layout_item, 'column_index', member_index + 1) or (member_index + 1)),
        )
        active_view_item.column_index, target_view_item.column_index = (
            int(getattr(target_view_item, 'column_index', target_member_index + 1) or (target_member_index + 1)),
            int(getattr(active_view_item, 'column_index', member_index + 1) or (member_index + 1)),
        )
        active_view_item.ui_order, target_view_item.ui_order = (
            int(getattr(target_view_item, 'ui_order', target_view_index + 1) or (target_view_index + 1)),
            int(getattr(active_view_item, 'ui_order', view_index + 1) or (view_index + 1)),
        )
        if row_header is not None:
            row_header.uid = next_header_uid
            row_header.row_member_uids_json = _izom_propui_free_json_dumps(next_member_uids)
        active_view_item.parent_uid = next_header_uid
        target_view_item.parent_uid = next_header_uid
        _izom_propui_free_swap_collection_items(layout_collection, layout_index, target_layout_index)
        _izom_propui_free_swap_collection_items(view_collection, view_index, target_view_index)
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
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
        layout_item_after, layout_index_after = _izom_propui_free_collection_item_and_index_by_uid(layout_collection, layout_uid)
        _view_item_after, view_index_after = _izom_propui_free_collection_item_and_index_by_uid(view_collection, view_uid)
        params.izom_propui_free_layout_active_index = max(0, layout_index_after)
        params.izom_propui_free_layout_active_uid = layout_uid if layout_item_after is not None else ''
        params.izom_propui_free_layout_selected_uids_json = _izom_propui_free_json_dumps([layout_uid])
        params.izom_propui_free_layout_selection_anchor_uid = layout_uid
        params.izom_propui_free_layout_view_active_index = max(0, view_index_after)
        params.izom_propui_free_layout_view_active_uid = view_uid
        params.izom_propui_free_layout_view_selected_uids_json = _izom_propui_free_json_dumps([view_uid])
        params.izom_propui_free_layout_view_selection_anchor_uid = view_uid
    finally:
        _izom_propui_free_resume_list_context_updates(params)
    return True, view_uid

def _izom_propui_free_set_layout_view_row_member_column_direct(params, view_item, requested_column):
    if params is None or view_item is None:
        return False, ''
    if str(getattr(view_item, 'kind', '') or '').strip() != 'ENTRY_ITEM':
        return False, ''

    layout_uid = str(getattr(view_item, 'layout_uid', '') or '').strip()
    row_header_uid = str(getattr(view_item, 'parent_uid', '') or '').strip()
    if not layout_uid or not row_header_uid.startswith('ROW_HEADER:'):
        return False, ''

    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if layout_collection is None or view_collection is None:
        return False, ''

    row_header = None
    for item in view_collection:
        if str(getattr(item, 'uid', '') or '').strip() == row_header_uid:
            row_header = item
            break
    member_uids = _izom_propui_free_layout_view_row_member_uids(row_header)
    if len(member_uids) <= 1 or layout_uid not in member_uids:
        return False, ''

    current_index = member_uids.index(layout_uid)
    try:
        target_index = max(0, min(len(member_uids) - 1, int(requested_column or 1) - 1))
    except (TypeError, ValueError):
        target_index = 0
    if target_index == current_index:
        return False, ''

    next_member_uids = list(member_uids)
    next_member_uids.pop(current_index)
    next_member_uids.insert(target_index, layout_uid)
    next_header_uid = _izom_propui_free_layout_view_row_uid(next_member_uids)

    member_uid_set = set(member_uids)
    layout_items = {}
    layout_indices = {}
    for index, item in enumerate(layout_collection):
        uid = str(getattr(item, 'uid', '') or '').strip()
        if uid in member_uid_set:
            layout_items[uid] = item
            layout_indices[uid] = index
            if len(layout_items) == len(member_uid_set):
                break
    if len(layout_items) != len(member_uid_set):
        return False, ''

    entry_view_uids = {
        _izom_propui_free_layout_view_entry_uid(uid): uid
        for uid in member_uids
    }
    view_items = {}
    view_indices = {}
    for index, item in enumerate(view_collection):
        uid = str(getattr(item, 'uid', '') or '').strip()
        layout_member_uid = entry_view_uids.get(uid)
        if layout_member_uid:
            view_items[layout_member_uid] = item
            view_indices[layout_member_uid] = index
            if len(view_items) == len(member_uid_set):
                break
    if len(view_items) != len(member_uid_set):
        return False, ''

    layout_target_uid = member_uids[target_index]
    view_uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
    target_view_uid = _izom_propui_free_layout_view_entry_uid(layout_target_uid)
    layout_index = layout_indices.get(layout_uid, -1)
    target_layout_index = layout_indices.get(layout_target_uid, -1)
    view_index = view_indices.get(layout_uid, -1)
    target_view_index = view_indices.get(layout_target_uid, -1)
    if min(layout_index, target_layout_index, view_index, target_view_index) < 0:
        return False, ''

    ordered_view_orders = [
        int(getattr(view_items[uid], 'ui_order', view_indices[uid] + 1) or (view_indices[uid] + 1))
        for uid in member_uids
    ]
    ordered_view_orders.sort()

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        for column_index, uid in enumerate(next_member_uids, start=1):
            layout_items[uid].column_index = column_index
            view_item_for_uid = view_items[uid]
            view_item_for_uid.column_index = column_index
            view_item_for_uid.parent_uid = next_header_uid
            view_item_for_uid.ui_order = ordered_view_orders[column_index - 1]
        if row_header is not None:
            row_header.uid = next_header_uid
            row_header.row_member_uids_json = _izom_propui_free_json_dumps(next_member_uids)
        _izom_propui_free_swap_collection_items(layout_collection, layout_index, target_layout_index)
        _izom_propui_free_swap_collection_items(view_collection, view_index, target_view_index)
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
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
        _izom_propui_free_set_simple_layout_view_selection_direct(params, view_uid, layout_uid=layout_uid)
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    return True, view_uid

def _izom_propui_free_remove_layout_item_for_entry_direct(params, entry_uids):
    if params is None:
        return False
    target_entry_uids = {
        str(uid or '').strip()
        for uid in (entry_uids or ())
        if str(uid or '').strip()
    }
    if not target_entry_uids:
        return False

    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    matches = []
    items_by_row = {}
    target_row_key = None
    row_layout_items = []
    for index, item in enumerate(layout_collection or ()):
        try:
            item_row_index = int(getattr(item, 'row_index', 1) or 1)
        except (TypeError, ValueError):
            item_row_index = 1
        row_key = item_row_index
        if target_row_key is None:
            items_by_row.setdefault(row_key, []).append(item)
        elif row_key == target_row_key:
            row_layout_items.append(item)
        if str(getattr(item, 'entry_uid', '') or '').strip() in target_entry_uids:
            matches.append((item, index))
            if target_row_key is None:
                target_row_key = row_key
                row_layout_items = list(items_by_row.get(row_key, ()))
    if len(matches) != 1:
        return False

    layout_item, layout_index = matches[0]
    layout_uid = str(getattr(layout_item, 'uid', '') or '').strip()
    if not layout_uid:
        return False
    row_index = target_row_key or int(getattr(layout_item, 'row_index', 1) or 1)
    if len(row_layout_items) <= 1:
        return False
    row_layout_items.sort(key=lambda item: int(getattr(item, 'column_index', 1) or 1))
    remaining_layout_uids = [
        str(getattr(item, 'uid', '') or '').strip()
        for item in row_layout_items
        if str(getattr(item, 'uid', '') or '').strip() and str(getattr(item, 'uid', '') or '').strip() != layout_uid
    ]
    if not remaining_layout_uids:
        return False
    row_layout_by_uid = {
        str(getattr(item, 'uid', '') or '').strip(): item
        for item in row_layout_items
        if str(getattr(item, 'uid', '') or '').strip()
    }

    if not view_collection:
        guard_key = _izom_propui_free_suspend_list_context_updates(params)
        try:
            layout_collection.remove(layout_index)
            for column_index, member_uid in enumerate(remaining_layout_uids, start=1):
                member_item = row_layout_by_uid.get(member_uid)
                if member_item is not None:
                    member_item.column_index = column_index
            _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
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
            _izom_propui_free_resume_list_context_updates(params)
        return True

    view_uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
    view_by_uid = {
        str(getattr(item, 'uid', '') or '').strip(): (item, index)
        for index, item in enumerate(view_collection or ())
        if str(getattr(item, 'uid', '') or '').strip()
    }
    view_item, view_index = view_by_uid.get(view_uid, (None, -1))
    if view_item is None:
        return False
    row_header_uid = str(getattr(view_item, 'parent_uid', '') or '').strip()
    if not row_header_uid.startswith('ROW_HEADER:'):
        return False
    row_header, row_header_index = view_by_uid.get(row_header_uid, (None, -1))
    member_uids = _izom_propui_free_layout_view_row_member_uids(row_header)
    if layout_uid not in member_uids or len(member_uids) <= 1:
        return False

    remaining_member_uids = [uid for uid in member_uids if uid != layout_uid]
    next_header_uid = _izom_propui_free_layout_view_row_uid(remaining_member_uids) if len(remaining_member_uids) > 1 else ''

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        layout_collection.remove(layout_index)
        if len(remaining_member_uids) > 1 and row_header is not None:
            row_header.uid = next_header_uid
            row_header.row_member_uids_json = _izom_propui_free_json_dumps(remaining_member_uids)
        elif row_header_index >= 0:
            view_collection.remove(row_header_index)
            if row_header_index < view_index:
                view_index -= 1
        if view_index >= 0:
            view_collection.remove(view_index)

        for column_index, member_uid in enumerate(remaining_member_uids, start=1):
            member_item = row_layout_by_uid.get(member_uid)
            member_view, _member_view_index = view_by_uid.get(
                _izom_propui_free_layout_view_entry_uid(member_uid),
                (None, -1),
            )
            if member_item is not None:
                member_item.column_index = column_index
            if member_view is not None:
                member_view.column_index = column_index
                member_view.parent_uid = next_header_uid

        for ui_order, item in enumerate(view_collection or (), start=1):
            try:
                item.ui_order = ui_order
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )

        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
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
        _izom_propui_free_resume_list_context_updates(params)
    return True


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
