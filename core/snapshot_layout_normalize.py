# SPDX-License-Identifier: GPL-3.0-or-later

from .snapshot_layout_common import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS,
    _IZOM_PROPUI_FREE_LAYOUT_ROW_FIELD_DEFAULTS,
    _izom_propui_free_apply_layout_rows_to_snapshots,
    _izom_propui_free_layout_flag_enabled,
    _izom_propui_free_layout_rows_from_layout_snapshots,
    _izom_propui_free_new_uid,
)


def _izom_propui_free_layout_row_count(layout_snapshots):
    if not layout_snapshots:
        return 0
    return max(max(1, int(snap['row_index'] or 1)) for snap in layout_snapshots)


def _izom_propui_free_layout_rows_from_snapshots_by_index(layout_snapshots, *, snapshots_are_ordered=False):
    rows = []
    current_row_index = None
    current_row = []
    source_snapshots = [dict(item) for item in (layout_snapshots or [])]
    if not bool(snapshots_are_ordered):
        source_snapshots.sort(
            key=lambda item: (
                max(1, int(item.get('row_index', 1) or 1)),
                max(1, int(item.get('column_index', 1) or 1)),
            )
        )
    for snap in source_snapshots:
        row_index = max(1, int(snap.get('row_index', 1) or 1))
        if current_row_index is None or row_index != current_row_index:
            if current_row:
                rows.append(current_row)
            current_row_index = row_index
            current_row = [snap]
        else:
            current_row.append(snap)
    if current_row:
        rows.append(current_row)
    return rows


def _izom_propui_free_order_layout_rows_by_container(layout_snapshots, *, layout_snapshots_are_ordered=False):
    if not layout_snapshots:
        return []

    rows = []
    for row in _izom_propui_free_layout_rows_from_snapshots_by_index(
        layout_snapshots,
        snapshots_are_ordered=layout_snapshots_are_ordered,
    ):
        if not row:
            continue
        first = row[0]
        row_settings = {
            field_name: first.get(field_name, _IZOM_PROPUI_FREE_LAYOUT_ROW_FIELD_DEFAULTS.get(field_name))
            for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS
        }
        rows.append((row, row_settings))

    ordered = []
    for next_row_index, (row, row_settings) in enumerate(rows, start=1):
        for column_index, source in enumerate(row, start=1):
            item = dict(source)
            item['row_index'] = next_row_index
            item['column_index'] = column_index
            for field_name, field_value in row_settings.items():
                item[field_name] = field_value
            ordered.append(item)
    return ordered


def _izom_propui_free_normalize_layout_snapshots(layout_snapshots):
    if not layout_snapshots:
        return []

    normalized = []
    seen_uids = set()
    used_columns_by_row = {}
    for snap in layout_snapshots:
        item = dict(snap)
        layout_uid = str(item['uid'] or '').strip()
        if not layout_uid:
            raise ValueError("Layout snapshots must contain a non-empty uid")
        if layout_uid in seen_uids:
            layout_uid = _izom_propui_free_new_uid()
        seen_uids.add(layout_uid)
        item['uid'] = layout_uid
        item['entry_uid'] = str(item['entry_uid'] or '').strip()
        requested_row = max(1, int(item['row_index'] or 1))
        requested_column = max(1, int(item['column_index'] or 1))

        row_index = requested_row
        used_columns = used_columns_by_row.setdefault(row_index, set())
        column_index = requested_column
        while column_index in used_columns:
            column_index += 1

        used_columns.add(column_index)
        item['row_index'] = row_index
        item['column_index'] = column_index
        normalized.append(item)

    normalized.sort(
        key=lambda item: (
            int(item['row_index'] or 1),
            int(item['column_index'] or 1),
        )
    )
    applied = _izom_propui_free_apply_layout_rows_to_snapshots(
        normalized,
        _izom_propui_free_layout_rows_from_layout_snapshots(normalized),
    )
    return _izom_propui_free_order_layout_rows_by_container(
        applied,
        layout_snapshots_are_ordered=True,
    )

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
