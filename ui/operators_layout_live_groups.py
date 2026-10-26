# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_layout_live_core import (
    _izom_propui_free_apply_layout_row_fields_to_item,
    _izom_propui_free_collection_item_and_index_by_uid,
    _izom_propui_free_finish_direct_layout_row_edit,
    _izom_propui_free_layout_collapsed_row_uids,
    _izom_propui_free_layout_row_fields_from_item,
    _izom_propui_free_layout_uids_from_items,
    _izom_propui_free_layout_view_row_uid,
    _izom_propui_free_renumber_layout_view_order,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_row_item_and_index,
    _izom_propui_free_sort_layout_row_collection,
    _izom_propui_free_sorted_layout_items_for_rows,
    _izom_propui_free_suspend_list_context_updates,
    _izom_propui_free_view_row_header_by_members,
)
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from .helper_layout_rows import _izom_propui_free_layout_view_row_member_uids
from .operators_layout_view import _izom_propui_free_rebuild_layout_view_items



def _izom_propui_free_group_layout_item_adjacent_row_direct(params, view_item, direction):
    if params is None or view_item is None:
        return False, ''
    if str(getattr(view_item, 'kind', '') or '').strip() != 'ENTRY_ITEM':
        return False, ''
    if str(getattr(view_item, 'parent_uid', '') or '').strip().startswith('ROW_HEADER:'):
        return False, ''
    layout_uid = str(getattr(view_item, 'layout_uid', '') or '').strip()
    if not layout_uid:
        return False, ''

    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    row_collection = getattr(params, 'izom_propui_free_layout_rows', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if layout_collection is None or row_collection is None or view_collection is None:
        return False, ''

    layout_item, _layout_index = _izom_propui_free_collection_item_and_index_by_uid(layout_collection, layout_uid)
    if layout_item is None:
        return False, ''
    try:
        source_row = max(1, int(getattr(layout_item, 'row_index', 1) or 1))
    except (TypeError, ValueError):
        return False, ''
    direction = str(direction or 'RIGHT').strip().upper()
    if direction == 'LEFT':
        target_row = source_row - 1
        if target_row < 1:
            return False, ''
    elif direction == 'RIGHT':
        target_row = source_row + 1
    else:
        return False, ''

    row_items_by_index = _izom_propui_free_sorted_layout_items_for_rows(
        layout_collection,
        (source_row, target_row),
    )
    source_row_items = row_items_by_index.get(source_row, [])
    if len(source_row_items) != 1 or str(getattr(source_row_items[0], 'uid', '') or '').strip() != layout_uid:
        return False, ''

    target_row_items = row_items_by_index.get(target_row, [])
    if not target_row_items:
        return False, ''
    target_member_uids = _izom_propui_free_layout_uids_from_items(target_row_items)
    if len(target_member_uids) != len(target_row_items):
        return False, ''
    if len(target_member_uids) >= 3:
        return False, ''

    target_header = None
    if len(target_member_uids) > 1:
        target_header, _target_header_index = _izom_propui_free_view_row_header_by_members(view_collection, target_member_uids)
        if target_header is None:
            return False, ''
        if str(getattr(target_header, 'uid', '') or '').strip() in set(_izom_propui_free_layout_collapsed_row_uids(params)):
            return False, ''

    view_uid = _izom_propui_free_layout_view_entry_uid(layout_uid)
    active_view_item, active_view_index = _izom_propui_free_collection_item_and_index_by_uid(view_collection, view_uid)
    if active_view_item is None or active_view_index < 0:
        return False, ''

    if direction == 'RIGHT':
        new_member_uids = [layout_uid, *target_member_uids]
        row_fields = _izom_propui_free_layout_row_fields_from_item(layout_item)
        combined_row = source_row
        removed_row = target_row
    else:
        new_member_uids = [*target_member_uids, layout_uid]
        row_fields = _izom_propui_free_layout_row_fields_from_item(target_row_items[0])
        combined_row = target_row
        removed_row = source_row
    new_header_uid = _izom_propui_free_layout_view_row_uid(new_member_uids)
    layout_member_uid_set = set(new_member_uids)

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        if direction == 'RIGHT':
            layout_item.row_index = combined_row
            layout_item.column_index = 1
            _izom_propui_free_apply_layout_row_fields_to_item(layout_item, row_fields)
            for column_index, member_item in enumerate(target_row_items, start=2):
                member_item.row_index = combined_row
                member_item.column_index = column_index
                _izom_propui_free_apply_layout_row_fields_to_item(member_item, row_fields)
        else:
            for column_index, member_item in enumerate(target_row_items, start=1):
                member_item.row_index = combined_row
                member_item.column_index = column_index
                _izom_propui_free_apply_layout_row_fields_to_item(member_item, row_fields)
            layout_item.row_index = combined_row
            layout_item.column_index = len(target_row_items) + 1
            _izom_propui_free_apply_layout_row_fields_to_item(layout_item, row_fields)
        layout_row_count = 0
        for item in layout_collection:
            item_uid = str(getattr(item, 'uid', '') or '').strip()
            try:
                item_row = max(1, int(getattr(item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if item_uid not in layout_member_uid_set and item_row > removed_row:
                item.row_index = item_row - 1
                item_row -= 1
            layout_row_count = max(layout_row_count, item_row)

        _row_item, row_remove_index = _izom_propui_free_row_item_and_index(row_collection, removed_row)
        if row_remove_index >= 0:
            row_collection.remove(row_remove_index)
        for row_item in row_collection:
            try:
                item_row = max(1, int(getattr(row_item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if item_row > removed_row:
                row_item.row_index = item_row - 1
        _izom_propui_free_sort_layout_row_collection(row_collection)

        _izom_propui_free_rebuild_layout_view_items(
            params,
            preferred_active_uid=view_uid,
            sync_selection=False,
        )
        _izom_propui_free_finish_direct_layout_row_edit(
            params,
            layout_collection,
            selected_view_uid=view_uid,
        )
    finally:
        _izom_propui_free_resume_list_context_updates(params)
    return True, view_uid

def _izom_propui_free_ungroup_layout_row_direct(params, view_item):
    if params is None or view_item is None:
        return False, ''
    if str(getattr(view_item, 'kind', '') or '').strip() != 'ROW_HEADER':
        return False, ''
    member_uids = _izom_propui_free_layout_view_row_member_uids(view_item)
    if len(member_uids) <= 1:
        return False, ''

    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    row_collection = getattr(params, 'izom_propui_free_layout_rows', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if layout_collection is None or row_collection is None or view_collection is None:
        return False, ''

    header_uid = str(getattr(view_item, 'uid', '') or '').strip()
    if header_uid in set(_izom_propui_free_layout_collapsed_row_uids(params)):
        return False, ''
    try:
        source_row = max(1, int(getattr(view_item, 'row_index', 1) or 1))
    except (TypeError, ValueError):
        return False, ''
    member_uid_set = set(member_uids)
    layout_item_by_uid = {}
    for item in layout_collection:
        item_uid = str(getattr(item, 'uid', '') or '').strip()
        if item_uid in member_uid_set:
            layout_item_by_uid[item_uid] = item
            if len(layout_item_by_uid) == len(member_uid_set):
                break
    layout_items = []
    for uid in member_uids:
        item = layout_item_by_uid.get(uid)
        if item is None:
            return False, ''
        layout_items.append(item)

    header_item = None
    header_index = -1
    entry_view_by_layout_uid = {}
    for index, item in enumerate(view_collection):
        item_uid = str(getattr(item, 'uid', '') or '').strip()
        if item_uid == header_uid:
            header_item = item
            header_index = index
        if str(getattr(item, 'kind', '') or '').strip() == 'ENTRY_ITEM':
            layout_uid = str(getattr(item, 'layout_uid', '') or '').strip()
            if layout_uid in member_uid_set:
                entry_view_by_layout_uid[layout_uid] = (item, index)
        if header_item is not None and len(entry_view_by_layout_uid) == len(member_uid_set):
            break
    entry_views = [entry_view_by_layout_uid.get(uid, (None, -1)) for uid in member_uids]
    if any(item is None for item, _index in entry_views):
        return False, ''
    if header_item is None or header_index < 0:
        return False, ''

    source_row_item, _source_row_index = _izom_propui_free_row_item_and_index(row_collection, source_row)
    row_fields = _izom_propui_free_layout_row_fields_from_item(source_row_item or layout_items[0])
    shift = len(member_uids) - 1
    selected_view_uid = _izom_propui_free_layout_view_entry_uid(member_uids[0])

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        for offset, item in enumerate(layout_items):
            item.row_index = source_row + offset
            item.column_index = 1
            _izom_propui_free_apply_layout_row_fields_to_item(item, row_fields)
        layout_row_count = 0
        for item in layout_collection:
            item_uid = str(getattr(item, 'uid', '') or '').strip()
            try:
                item_row = max(1, int(getattr(item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if item_uid not in member_uid_set and item_row > source_row:
                item.row_index = item_row + shift
                item_row += shift
            layout_row_count = max(layout_row_count, item_row)

        for row_item in row_collection:
            try:
                item_row = max(1, int(getattr(row_item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if item_row > source_row:
                row_item.row_index = item_row + shift
        for offset in range(1, len(member_uids)):
            row_item = row_collection.add()
            row_item.row_index = source_row + offset
            _izom_propui_free_apply_layout_row_fields_to_item(row_item, row_fields)
        _izom_propui_free_sort_layout_row_collection(row_collection)

        view_collection.remove(header_index)
        for offset, (entry_view, _index) in enumerate(entry_views):
            entry_view.parent_uid = ''
            entry_view.row_index = source_row + offset
            entry_view.column_index = 1
            entry_view.row_member_uids_json = '[]'
        entry_view_uid_set = {
            _izom_propui_free_layout_view_entry_uid(uid)
            for uid in member_uids
        }
        for item in view_collection:
            if str(getattr(item, 'uid', '') or '').strip() in entry_view_uid_set:
                continue
            try:
                item_row = max(1, int(getattr(item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if item_row > source_row:
                item.row_index = item_row + shift
        _izom_propui_free_renumber_layout_view_order(view_collection)
        _izom_propui_free_finish_direct_layout_row_edit(
            params,
            layout_collection,
            selected_view_uid=selected_view_uid,
        )
    finally:
        _izom_propui_free_resume_list_context_updates(params)
    return True, selected_view_uid


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
