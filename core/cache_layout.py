# SPDX-License-Identifier: GPL-3.0-or-later

from .cache_entries import (
    _izom_propui_free_cache_public,
    _izom_propui_free_cached_params_field,
)
from .constants_display import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN,
)
from .text import izom_propui_free_entry_display_name



def _izom_propui_free_build_layout_item_lookup(params):
    by_uid = {}
    by_entry_uid = {}
    index_by_uid = {}
    ordered_uids = []
    seen_uids = set()
    for index, item in enumerate(getattr(params, 'izom_propui_free_layout_items', []) or []):
        layout_uid = str(getattr(item, 'uid', '') or '').strip()
        entry_uid = str(getattr(item, 'entry_uid', '') or '').strip()
        if layout_uid:
            by_uid[layout_uid] = item
            index_by_uid[layout_uid] = index
            if layout_uid not in seen_uids:
                ordered_uids.append(layout_uid)
                seen_uids.add(layout_uid)
        if layout_uid and entry_uid and entry_uid not in by_entry_uid:
            by_entry_uid[entry_uid] = item
    return {
        'by_uid': by_uid,
        'by_entry_uid': by_entry_uid,
        'index_by_uid': index_by_uid,
        'ordered_uids': tuple(ordered_uids),
    }


def izom_propui_free_cached_layout_item_lookup(params):
    if params is None:
        return {
            'by_uid': {},
            'by_entry_uid': {},
            'index_by_uid': {},
            'ordered_uids': (),
        }
    build_layout_item_lookup = _izom_propui_free_cache_public(
        '_izom_propui_free_build_layout_item_lookup',
        _izom_propui_free_build_layout_item_lookup,
    )
    return _izom_propui_free_cached_params_field(
        params,
        'layout_item_lookup',
        lambda: build_layout_item_lookup(params),
    )


def _izom_propui_free_build_visible_layout_rows(layout_snapshots):
    ordered = []
    for order_index, snap in enumerate(layout_snapshots or []):
        layout_uid = str(snap.get('uid', '') or '').strip()
        entry_uid = str(snap.get('entry_uid', '') or '').strip()
        if not layout_uid or not entry_uid:
            continue
        try:
            row_index = max(1, int(snap.get('row_index', 1) or 1))
        except (TypeError, ValueError):
            row_index = 1
        try:
            column_index = max(1, int(snap.get('column_index', 1) or 1))
        except (TypeError, ValueError):
            column_index = 1
        ordered.append((row_index, column_index, order_index, layout_uid))

    ordered.sort(key=lambda item: (item[0], item[1], item[2]))

    rows = []
    current_row_index = None
    current_row = []
    for row_index, _column_index, _order_index, layout_uid in ordered:
        if current_row_index is None or row_index != current_row_index:
            if current_row:
                rows.append(tuple(current_row))
            current_row_index = row_index
            current_row = [layout_uid]
        else:
            current_row.append(layout_uid)
    if current_row:
        rows.append(tuple(current_row))
    return tuple(rows)


def _izom_propui_free_entry_snapshot_display_name(entry_snapshot, *, fallback_index=1):
    if not isinstance(entry_snapshot, dict):
        return f"Entry {int(fallback_index or 1)}"
    return izom_propui_free_entry_display_name(entry_snapshot, fallback_index=fallback_index)


def _izom_propui_free_generated_row_height_label(value):
    try:
        scale = float(value if value is not None else IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT)
    except (TypeError, ValueError):
        scale = float(IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT)
    label = f"{scale:.3f}".rstrip('0').rstrip('.')
    return f"H-{label or '1'}"


def _izom_propui_free_generated_row_inset_value(value):
    try:
        amount = float(value if value is not None else IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT)
    except (TypeError, ValueError):
        amount = float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT)
    return max(
        float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN),
        min(float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX), amount),
    )


def _izom_propui_free_generated_row_inset_label(layout_snapshot):
    if not isinstance(layout_snapshot, dict):
        return ''
    parts = []
    if bool(layout_snapshot.get('row_inset_left_enabled', False)):
        amount = _izom_propui_free_generated_row_inset_value(layout_snapshot.get('row_inset_left_amount'))
        parts.append(f"L-{f'{amount:.3f}'.rstrip('0').rstrip('.') or '1'}")
    return " ".join(parts)


def _izom_propui_free_generated_row_percent_labels(member_uids, layout_snapshot_by_uid):
    return {}


def _izom_propui_free_build_generated_layout_state(visible_layout_rows, layout_snapshots, entry_snapshots):
    groups = []
    group_by_row_index = {}
    row_by_layout_uid = {}
    shared_row_size_by_layout_uid = {}
    row_width_percent_label_by_layout_uid = {}
    row_height_label_by_layout_uid = {}
    row_height_label_by_row_index = {}
    row_inset_label_by_layout_uid = {}
    row_inset_label_by_row_index = {}
    ordered_layout_uids = []
    container_uid_by_row_index = {}
    row_indices_by_container_uid = {'': []}
    container_titles = {'': 'Main Panel Body'}
    layout_snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in (layout_snapshots or [])
        if str(snap.get('uid', '') or '').strip()
    }
    layout_entry_uid_by_uid = {
        str(snap.get('uid', '') or '').strip(): str(snap.get('entry_uid', '') or '').strip()
        for snap in (layout_snapshots or [])
        if str(snap.get('uid', '') or '').strip()
    }
    entry_snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in (entry_snapshots or [])
        if str(snap.get('uid', '') or '').strip()
    }

    for row_index, row_member_uids in enumerate(visible_layout_rows or (), start=1):
        member_uids = tuple(
            str(layout_uid or '').strip()
            for layout_uid in (row_member_uids or ())
            if str(layout_uid or '').strip()
        )
        if not member_uids:
            continue

        member_display_names = []
        first_entry_uid = ''
        for member_index, layout_uid in enumerate(member_uids, start=1):
            entry_uid = layout_entry_uid_by_uid.get(layout_uid, '')
            if entry_uid and not first_entry_uid:
                first_entry_uid = entry_uid
            member_display_names.append(
                _izom_propui_free_entry_snapshot_display_name(
                    entry_snapshot_by_uid.get(entry_uid),
                    fallback_index=member_index,
                )
            )

        preview_text = " | ".join(member_display_names)
        highlighted_preview_text_by_layout_uid = {
            highlighted_layout_uid: " | ".join(
                f"[{display_name}]" if current_layout_uid == highlighted_layout_uid else display_name
                for current_layout_uid, display_name in zip(member_uids, member_display_names)
            )
            for highlighted_layout_uid in member_uids
        }
        row_width_percent_label_by_layout_uid.update(
            _izom_propui_free_generated_row_percent_labels(
                member_uids,
                layout_snapshot_by_uid,
            )
        )
        first_layout_snapshot = layout_snapshot_by_uid.get(member_uids[0]) if member_uids else None
        row_height_label = _izom_propui_free_generated_row_height_label(
            first_layout_snapshot.get('row_height_scale') if isinstance(first_layout_snapshot, dict) else None
        )
        row_height_label_by_row_index[row_index] = row_height_label
        row_inset_label = _izom_propui_free_generated_row_inset_label(first_layout_snapshot)
        row_inset_label_by_row_index[row_index] = row_inset_label
        for layout_uid in member_uids:
            row_height_label_by_layout_uid[layout_uid] = row_height_label
            row_inset_label_by_layout_uid[layout_uid] = row_inset_label

        group = {
            'row_index': row_index,
            'member_uids': member_uids,
            'first_entry_uid': first_entry_uid,
            'preview_text': preview_text,
            'highlighted_preview_text_by_layout_uid': highlighted_preview_text_by_layout_uid,
        }
        container_uid_by_row_index[row_index] = ''
        row_indices_by_container_uid[''].append(row_index)
        groups.append(group)
        group_by_row_index[row_index] = group
        ordered_layout_uids.extend(member_uids)

        row_size = len(member_uids)
        for layout_uid in member_uids:
            row_by_layout_uid[layout_uid] = member_uids
            shared_row_size_by_layout_uid[layout_uid] = max(1, row_size)

    return {
        'rows': tuple(visible_layout_rows or ()),
        'groups': tuple(groups),
        'group_by_row_index': group_by_row_index,
        'row_by_layout_uid': row_by_layout_uid,
        'shared_row_size_by_layout_uid': shared_row_size_by_layout_uid,
        'row_width_percent_label_by_layout_uid': row_width_percent_label_by_layout_uid,
        'row_height_label_by_layout_uid': row_height_label_by_layout_uid,
        'row_height_label_by_row_index': row_height_label_by_row_index,
        'row_inset_label_by_layout_uid': row_inset_label_by_layout_uid,
        'row_inset_label_by_row_index': row_inset_label_by_row_index,
        'ordered_layout_uids': tuple(ordered_layout_uids),
        'container_uid_by_row_index': container_uid_by_row_index,
        'row_indices_by_container_uid': {
            container_uid: tuple(indices)
            for container_uid, indices in row_indices_by_container_uid.items()
        },
        'container_titles': container_titles,
    }


def _izom_propui_free_layout_snapshot_row_count(layout_snapshots):
    row_count = 0
    for snap in layout_snapshots or []:
        try:
            row_count = max(row_count, max(1, int(snap.get('row_index', 1) or 1)))
        except (TypeError, ValueError):
            continue
    return row_count


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
