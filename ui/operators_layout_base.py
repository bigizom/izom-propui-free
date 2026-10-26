# SPDX-License-Identifier: GPL-3.0-or-later


from ..core.constants import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
)
from ..core.context import izom_propui_free_context_params
from ..core.snapshots import (
    _izom_propui_free_order_layout_rows_by_container,
)
from ..core.snapshot_layout import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS,
)
from .helpers import (
    _izom_propui_free_layout_visible_snapshots,
    _izom_propui_free_ordered_layout_snapshots,
)


def _izom_propui_free_entry_params(context):
    return izom_propui_free_context_params(context)

def _izom_propui_free_snapshot_index_by_uid(snapshots):
    return {str(snap.get('uid', '') or ''): index for index, snap in enumerate(snapshots)}

def _izom_propui_free_layout_rows_from_items(
    layout_snapshots,
    *,
    params=None,
    visible_only=False,
    snapshots_are_ordered=False,
):
    ordered = (
        _izom_propui_free_layout_visible_snapshots(
            params,
            layout_snapshots,
            snapshots_are_ordered=bool(snapshots_are_ordered),
        )
        if visible_only
        else (
            list(layout_snapshots or [])
            if bool(snapshots_are_ordered)
            else _izom_propui_free_ordered_layout_snapshots(layout_snapshots)
        )
    )
    rows = []
    current_row_index = None
    current_row = []
    for snap in ordered:
        row_index = int(snap.get('row_index', 1) or 1)
        if current_row_index is None or row_index != current_row_index:
            if current_row:
                rows.append(current_row)
            current_row_index = row_index
            current_row = [str(snap.get('uid', '') or '').strip()]
        else:
            current_row.append(str(snap.get('uid', '') or '').strip())
    if current_row:
        rows.append(current_row)
    return rows

def _izom_propui_free_apply_layout_rows_to_items(
    layout_snapshots,
    rows,
    *,
    params=None,
    assume_container_order=False,
):
    snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in layout_snapshots or []
        if str(snap.get('uid', '') or '').strip()
    }
    ordered = []
    seen = set()
    compact_rows = []
    for row in rows or []:
        compact_row = []
        for uid in row or []:
            target_uid = str(uid or '').strip()
            if not target_uid or target_uid in seen or target_uid not in snapshot_by_uid:
                continue
            seen.add(target_uid)
            compact_row.append(target_uid)
        if compact_row:
            compact_rows.append(compact_row)

    for snap in layout_snapshots or []:
        uid = str(snap.get('uid', '') or '').strip()
        if not uid or uid in seen:
            continue
        compact_rows.append([uid])

    for row_index, row in enumerate(compact_rows, start=1):
        row_source = snapshot_by_uid.get(row[0]) if row else None
        row_settings = {
            field_name: row_source.get(field_name)
            for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS
        } if row_source is not None else {}
        for column_index, uid in enumerate(row, start=1):
            snap = snapshot_by_uid.get(uid)
            if snap is None:
                continue
            snap['row_index'] = row_index
            snap['column_index'] = column_index
            for field_name, field_value in row_settings.items():
                if field_value is not None:
                    snap[field_name] = field_value
            ordered.append(snap)

    ordered_uids = {str(snap.get('uid', '') or '').strip() for snap in ordered}
    leftovers = [snap for snap in layout_snapshots or [] if str(snap.get('uid', '') or '').strip() not in ordered_uids]
    resolved = ordered + leftovers
    if bool(assume_container_order):
        return resolved
    return _izom_propui_free_order_layout_rows_by_container(
        resolved,
        layout_snapshots_are_ordered=True,
    )

def _izom_propui_free_rows_by_layout_container(visible_snapshots, snapshot_by_uid=None):
    rows = []
    current_row_index = None
    current_row = []

    def flush_current_row():
        if current_row:
            rows.append(current_row.copy())

    for snap in visible_snapshots or ():
        uid = str((snap or {}).get('uid', '') or '').strip()
        if not uid:
            continue
        try:
            row_index = max(1, int((snap or {}).get('row_index', 1) or 1))
        except (TypeError, ValueError):
            row_index = 1
        if current_row_index is None:
            current_row_index = row_index
        elif row_index != current_row_index:
            flush_current_row()
            current_row_index = row_index
            current_row = []
        current_row.append(uid)
    flush_current_row()
    return {'': rows}

def _izom_propui_free_insert_layout_uid_at_row_end(rows, row_index, item_uid):
    target_uid = str(item_uid or '').strip()
    if not target_uid:
        return
    row_index = max(0, int(row_index or 0))
    if row_index >= len(rows):
        rows.append([target_uid])
        return
    rows[row_index].append(target_uid)

def _izom_propui_free_layout_row_container_uid(row, snapshot_by_uid):
    return ''

def _izom_propui_free_layout_rows_share_container(row_a, row_b, snapshot_by_uid):
    return (
        _izom_propui_free_layout_row_container_uid(row_a, snapshot_by_uid)
        == _izom_propui_free_layout_row_container_uid(row_b, snapshot_by_uid)
    )

def _izom_propui_free_make_fast_ordered_layout_snapshot(index_hint, entry_uid):
    row_index = max(1, int(index_hint or 1))
    clean_entry_uid = str(entry_uid or '').strip()
    return {
        'uid': f"layout_{row_index}_{clean_entry_uid}",
        'entry_uid': clean_entry_uid,
        'row_index': row_index,
        'column_index': 1,
        'row_height_scale': IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
        'row_inset_left_enabled': False,
        'row_inset_left_amount': IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
    }


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
