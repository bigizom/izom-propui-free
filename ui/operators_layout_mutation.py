# SPDX-License-Identifier: GPL-3.0-or-later


from .operators_layout_live_core import (
    _izom_propui_free_layout_item_position,
)
from ..core.entry_ids import _izom_propui_free_new_uid
from ..core.snapshot_layout_ensure import _izom_propui_free_layout_view_entry_uid
from .helper_layout_rows import _izom_propui_free_layout_view_row_member_uids
from .operators_layout_base import (
    _izom_propui_free_apply_layout_rows_to_items,
    _izom_propui_free_insert_layout_uid_at_row_end,
    _izom_propui_free_layout_rows_from_items,
    _izom_propui_free_layout_rows_share_container,
)



def _izom_propui_free_move_layout_row(layout_snapshots, row_number, direction, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(layout_snapshots, params=params, visible_only=True)
    row_index = max(0, int(row_number or 1) - 1)
    if row_index < 0 or row_index >= len(rows):
        return False
    direction = str(direction or 'UP').strip().upper()
    if direction == 'UP':
        if row_index <= 0:
            return False
        target_index = row_index - 1
    else:
        if row_index >= len(rows) - 1:
            return False
        target_index = row_index + 1
    rows[row_index], rows[target_index] = rows[target_index], rows[row_index]
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True

def _izom_propui_free_move_layout_view_item_one_level(layout_snapshots, view_item, direction, *, params=None):
    if view_item is None:
        return False, ''
    direction = str(direction or 'UP').strip().upper()
    if direction not in {'UP', 'DOWN'}:
        return False, ''

    if str(getattr(view_item, 'kind', '') or '').strip() == 'ROW_HEADER':
        member_uids = _izom_propui_free_layout_view_row_member_uids(view_item)
        if not member_uids:
            return False, ''
        moved = _izom_propui_free_move_layout_row(
            layout_snapshots,
            int(getattr(view_item, 'row_index', 1) or 1),
            direction,
            params=params,
        )
        return moved, str(getattr(view_item, 'uid', '') or '').strip()

    layout_uid = str(getattr(view_item, 'layout_uid', '') or '').strip()
    if not layout_uid:
        return False, ''
    rows = _izom_propui_free_layout_rows_from_items(layout_snapshots, params=params, visible_only=True)
    row_index, column_index = _izom_propui_free_layout_item_position(rows, layout_uid)
    if row_index < 0:
        return False, ''
    row = rows[row_index]
    if len(row) <= 1:
        moved = _izom_propui_free_move_layout_row(layout_snapshots, row_index + 1, direction, params=params)
        return moved, _izom_propui_free_layout_view_entry_uid(layout_uid)
    if direction == 'UP':
        if column_index <= 0:
            return False, ''
        row[column_index - 1], row[column_index] = row[column_index], row[column_index - 1]
    else:
        if column_index >= len(row) - 1:
            return False, ''
        row[column_index], row[column_index + 1] = row[column_index + 1], row[column_index]
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True, _izom_propui_free_layout_view_entry_uid(layout_uid)

def _izom_propui_free_group_layout_item_into_previous_row(layout_snapshots, item_uid, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(
        layout_snapshots,
        params=params,
        visible_only=True,
        snapshots_are_ordered=True,
    )
    target_uid = str(item_uid or '').strip()
    row_index, column_index = _izom_propui_free_layout_item_position(rows, target_uid)
    if row_index <= 0 or column_index < 0:
        return False
    row = rows[row_index]
    if len(row) != 1 or column_index != 0:
        return False
    previous_row = rows[row_index - 1]
    if len(previous_row) >= 3:
        return False
    snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in layout_snapshots or []
        if str(snap.get('uid', '') or '').strip()
    }
    if not _izom_propui_free_layout_rows_share_container(row, previous_row, snapshot_by_uid):
        return False
    previous_row.append(target_uid)
    del rows[row_index]
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True

def _izom_propui_free_group_layout_item_into_next_row(layout_snapshots, item_uid, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(
        layout_snapshots,
        params=params,
        visible_only=True,
        snapshots_are_ordered=True,
    )
    target_uid = str(item_uid or '').strip()
    row_index, column_index = _izom_propui_free_layout_item_position(rows, target_uid)
    if row_index < 0 or column_index < 0 or row_index >= len(rows) - 1:
        return False
    row = rows[row_index]
    if len(row) != 1 or column_index != 0:
        return False
    next_row = rows[row_index + 1]
    if len(next_row) >= 3:
        return False
    snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in layout_snapshots or []
        if str(snap.get('uid', '') or '').strip()
    }
    if not _izom_propui_free_layout_rows_share_container(row, next_row, snapshot_by_uid):
        return False
    next_row.insert(0, target_uid)
    del rows[row_index]
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True

def _izom_propui_free_ungroup_layout_child_to_top_level(layout_snapshots, item_uid, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(
        layout_snapshots,
        params=params,
        visible_only=True,
        snapshots_are_ordered=True,
    )
    target_uid = str(item_uid or '').strip()
    row_index, column_index = _izom_propui_free_layout_item_position(rows, target_uid)
    if row_index < 0 or column_index < 0:
        return False
    row = rows[row_index]
    if len(row) <= 1:
        return False
    row.pop(column_index)
    rows.insert(row_index + 1, [target_uid])
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True

def _izom_propui_free_ungroup_layout_child_to_top_level_before(layout_snapshots, item_uid, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(
        layout_snapshots,
        params=params,
        visible_only=True,
        snapshots_are_ordered=True,
    )
    target_uid = str(item_uid or '').strip()
    row_index, column_index = _izom_propui_free_layout_item_position(rows, target_uid)
    if row_index < 0 or column_index < 0:
        return False
    row = rows[row_index]
    if len(row) <= 1:
        return False
    row.pop(column_index)
    rows.insert(row_index, [target_uid])
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True

def _izom_propui_free_ungroup_layout_row(layout_snapshots, row_number, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(
        layout_snapshots,
        params=params,
        visible_only=True,
        snapshots_are_ordered=True,
    )
    row_index = max(0, int(row_number or 1) - 1)
    if row_index < 0 or row_index >= len(rows):
        return False
    row = [str(uid or '').strip() for uid in rows[row_index] if str(uid or '').strip()]
    if len(row) <= 1:
        return False
    rows[row_index:row_index + 1] = [[uid] for uid in row]
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return True

def _izom_propui_free_duplicate_layout_row(layout_snapshots, row_number, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(
        layout_snapshots,
        params=params,
        visible_only=True,
        snapshots_are_ordered=True,
    )
    row_index = max(0, int(row_number or 1) - 1)
    if row_index < 0 or row_index >= len(rows):
        return []
    row = [str(uid or '').strip() for uid in rows[row_index] if str(uid or '').strip()]
    if not row:
        return []
    snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in layout_snapshots or []
        if str(snap.get('uid', '') or '').strip()
    }
    duplicated_snapshots = []
    duplicated_uids = []
    for uid in row:
        source = snapshot_by_uid.get(uid)
        if source is None:
            continue
        duplicated = dict(source)
        duplicated['uid'] = _izom_propui_free_new_uid()
        duplicated_snapshots.append(duplicated)
        duplicated_uids.append(duplicated['uid'])
    if not duplicated_snapshots:
        return []
    layout_snapshots.extend(duplicated_snapshots)
    rows.insert(row_index + 1, duplicated_uids)
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
        layout_snapshots,
        rows,
        params=params,
        assume_container_order=True,
    )
    return duplicated_uids

def _izom_propui_free_reinsert_layout_item_at_row(layout_snapshots, item_uid, requested_row, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(layout_snapshots, params=params, visible_only=bool(params))
    target_uid = str(item_uid or '').strip()
    current_row_index, _column_index = _izom_propui_free_layout_item_position(rows, target_uid)
    if current_row_index < 0:
        return False
    requested_row_index = max(0, int(requested_row or 1) - 1)
    if requested_row_index == current_row_index:
        return False

    row = rows[current_row_index]
    row.remove(target_uid)
    if not row:
        del rows[current_row_index]
    requested_row_index = min(requested_row_index, len(rows))
    if requested_row_index >= len(rows):
        rows.append([target_uid])
    else:
        _izom_propui_free_insert_layout_uid_at_row_end(rows, requested_row_index, target_uid)
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(layout_snapshots, rows, params=params)
    return True

def _izom_propui_free_reposition_layout_item_column(layout_snapshots, item_uid, requested_column, *, params=None):
    rows = _izom_propui_free_layout_rows_from_items(layout_snapshots, params=params, visible_only=bool(params))
    target_uid = str(item_uid or '').strip()
    row_index, column_index = _izom_propui_free_layout_item_position(rows, target_uid)
    if row_index < 0:
        return False
    row = rows[row_index]
    if len(row) <= 1:
        return False
    requested_index = max(0, min(len(row) - 1, int(requested_column or 1) - 1))
    if requested_index == column_index:
        return False
    row.pop(column_index)
    row.insert(requested_index, target_uid)
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(layout_snapshots, rows, params=params)
    return True

def _izom_propui_free_remove_layout_snapshots_by_entry_uids(layout_snapshots, entry_uids, *, params=None):
    removed = False
    target_uids = {str(uid or '').strip() for uid in (entry_uids or []) if str(uid or '').strip()}
    if not target_uids:
        return False
    filtered = []
    for snap in layout_snapshots:
        if str(snap.get('entry_uid', '') or '').strip() in target_uids:
            removed = True
            continue
        filtered.append(dict(snap))
    if removed:
        layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
            filtered,
            _izom_propui_free_layout_rows_from_items(filtered, params=params, visible_only=bool(params)),
            params=params,
        )
    return removed

def _izom_propui_free_remove_layout_snapshots_by_uids(layout_snapshots, layout_uids, *, params=None):
    removed = False
    target_uids = {str(uid or '').strip() for uid in (layout_uids or []) if str(uid or '').strip()}
    if not target_uids:
        return False
    filtered = []
    for snap in layout_snapshots:
        if str(snap.get('uid', '') or '').strip() in target_uids:
            removed = True
            continue
        filtered.append(dict(snap))
    if removed:
        layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(
            filtered,
            _izom_propui_free_layout_rows_from_items(filtered, params=params, visible_only=bool(params)),
            params=params,
        )
    return removed


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
