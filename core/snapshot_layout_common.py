# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import izom_propui_free_log_recovered
from contextlib import contextmanager

from .constants import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN,
)
from .entry_ids import _izom_propui_free_new_uid

_IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS = (AttributeError, TypeError, ValueError, ReferenceError)
_IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS = (ImportError, AttributeError)
IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS = (
    'row_height_scale',
    'row_inset_left_enabled',
    'row_inset_left_amount',
)
_IZOM_PROPUI_FREE_LAYOUT_ROW_FIELD_DEFAULTS = {
    'row_height_scale': IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    'row_inset_left_enabled': False,
    'row_inset_left_amount': IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
}


@contextmanager
def _izom_propui_free_suspended_list_context(params):
    ui_helpers = None
    try:
        from ..ui import helpers as _izom_propui_free_ui_helpers

        ui_helpers = _izom_propui_free_ui_helpers
        ui_helpers._izom_propui_free_suspend_list_context_updates(params)
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        ui_helpers = None
    try:
        yield ui_helpers
    finally:
        if ui_helpers is not None:
            ui_helpers._izom_propui_free_resume_list_context_updates(params)


def _izom_propui_free_restore_layout_selection_state(params, collection, active_index):
    try:
        if collection:
            active_index = max(0, min(active_index, len(collection) - 1))
            active_item_uid = getattr(collection[active_index], 'uid', '')
            params.izom_propui_free_layout_active_index = active_index
            params.izom_propui_free_layout_active_uid = active_item_uid
            params.izom_propui_free_layout_selected_uids_json = f'["{active_item_uid}"]'
            params.izom_propui_free_layout_selection_anchor_uid = active_item_uid
        else:
            params.izom_propui_free_layout_active_index = 0
            params.izom_propui_free_layout_active_uid = ''
            params.izom_propui_free_layout_selected_uids_json = "[]"
            params.izom_propui_free_layout_selection_anchor_uid = ''
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )


def _izom_propui_free_default_layout_row_fields():
    return dict(_IZOM_PROPUI_FREE_LAYOUT_ROW_FIELD_DEFAULTS)


def _izom_propui_free_layout_column_label(column_index, row_size=3):
    size = max(1, int(row_size or 1))
    column = max(1, min(size, int(column_index or 1)))
    return str(column)

def _izom_propui_free_make_default_layout_snapshot(index_hint, entry_uid=''):
    return {
        'uid': _izom_propui_free_new_uid(),
        'entry_uid': str(entry_uid or '').strip(),
        'row_index': max(1, int(index_hint or 1)),
        'column_index': 1,
        **_izom_propui_free_default_layout_row_fields(),
    }


def _izom_propui_free_make_default_layout_row_snapshot(index_hint):
    return {
        'row_index': max(1, int(index_hint or 1)),
        **_izom_propui_free_default_layout_row_fields(),
    }


def _izom_propui_free_layout_row_height_scale(value, default=IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT):
    try:
        numeric = float(value if value is not None else default)
    except (TypeError, ValueError):
        numeric = float(default)
    return max(
        IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN,
        min(IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX, numeric),
    )


def _izom_propui_free_layout_flag_enabled(value):
    return bool(value)


_izom_propui_free_layout_row_inset_enabled = _izom_propui_free_layout_flag_enabled


def _izom_propui_free_layout_row_inset_amount(value, default=IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT):
    return float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT)


def _izom_propui_free_layout_row_width_enabled(value):
    return False


def _izom_propui_free_layout_single_row_width(value, default=1.0):
    return 1.0


def _izom_propui_free_layout_single_row_alignment(value, default='LEFT'):
    return 'LEFT'


def _izom_propui_free_layout_row_field_values(source):
    item = source if isinstance(source, dict) else {}
    return {
        'row_height_scale': _izom_propui_free_layout_row_height_scale(
            item.get('row_height_scale', IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT)
        ),
        'row_inset_left_enabled': _izom_propui_free_layout_row_inset_enabled(item.get('row_inset_left_enabled', False)),
        'row_inset_left_amount': _izom_propui_free_layout_row_inset_amount(
            item.get('row_inset_left_amount', IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT)
        ),
    }


def _izom_propui_free_layout_row_snapshot_values(source, row_index=None):
    item = source if isinstance(source, dict) else {}
    resolved_row_index = max(1, int((row_index if row_index is not None else item.get('row_index', 1)) or 1))
    return {
        'row_index': resolved_row_index,
        **_izom_propui_free_layout_row_field_values(item),
    }


def _izom_propui_free_snapshot_layout_row(item):
    return _izom_propui_free_layout_row_snapshot_values({
        'row_index': getattr(item, 'row_index', 1),
        **{
            field_name: getattr(item, field_name, default_value)
            for field_name, default_value in _IZOM_PROPUI_FREE_LAYOUT_ROW_FIELD_DEFAULTS.items()
        },
    })


def izom_propui_free_snapshot_layout_rows(params):
    collection = getattr(params, 'izom_propui_free_layout_rows', None) or []
    normalized = {}
    for item in collection:
        snap = _izom_propui_free_snapshot_layout_row(item)
        normalized.setdefault(snap['row_index'], snap)
    return [normalized[row_index] for row_index in sorted(normalized)]


def _izom_propui_free_layout_rows_from_layout_snapshots(layout_snapshots, *, row_snapshots=None):
    row_by_index = {}
    for snap in row_snapshots or []:
        normalized = _izom_propui_free_layout_row_snapshot_values(snap)
        row_by_index.setdefault(normalized['row_index'], normalized)
    for snap in layout_snapshots or []:
        row_index = max(1, int(snap.get('row_index', 1) or 1))
        if row_index not in row_by_index:
            row_by_index[row_index] = _izom_propui_free_layout_row_snapshot_values(snap, row_index=row_index)
    return [row_by_index[row_index] for row_index in sorted(row_by_index)]


def _izom_propui_free_apply_layout_rows_to_snapshots(layout_snapshots, row_snapshots):
    row_by_index = {
        snap['row_index']: _izom_propui_free_layout_row_snapshot_values(snap)
        for snap in row_snapshots or []
    }
    resolved = []
    for snap in layout_snapshots or []:
        item = dict(snap)
        row_index = max(1, int(item.get('row_index', 1) or 1))
        row_snapshot = row_by_index.get(row_index) or _izom_propui_free_make_default_layout_row_snapshot(row_index)
        item.update({
            'row_index': row_index,
            **{field_name: row_snapshot[field_name] for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS},
        })
        resolved.append(item)
    return resolved


def _izom_propui_free_snapshot_layout_item(item):
    uid = str(getattr(item, 'uid', '') or '').strip() or _izom_propui_free_new_uid()
    entry_uid = str(getattr(item, 'entry_uid', '') or '').strip()
    row_index = max(1, int(getattr(item, 'row_index', 1) or 1))
    raw_column_index = getattr(item, 'column_index', None)
    column_index = max(1, int(raw_column_index or 1))
    return {
        'uid': uid,
        'entry_uid': entry_uid,
        'row_index': row_index,
        'column_index': column_index,
    }

def izom_propui_free_snapshot_layout_items(params):
    collection = getattr(params, 'izom_propui_free_layout_items', None) or []
    item_snapshots = [_izom_propui_free_snapshot_layout_item(item) for item in collection]
    row_by_index = {
        snap['row_index']: snap
        for snap in izom_propui_free_snapshot_layout_rows(params)
    }
    joined = []
    for snap in item_snapshots:
        item = dict(snap)
        row_index = max(1, int(item.get('row_index', 1) or 1))
        row_snapshot = row_by_index.get(row_index)
        if row_snapshot is None:
            row_snapshot = _izom_propui_free_layout_row_snapshot_values(item, row_index=row_index)
            row_by_index[row_index] = row_snapshot
        item.update({
            'row_index': row_index,
            **{field_name: row_snapshot[field_name] for field_name in IZOM_PROPUI_FREE_LAYOUT_ROW_FIELDS},
        })
        joined.append(item)
    return sorted(joined, key=lambda item: (int(item.get('row_index', 1) or 1), int(item.get('column_index', 1) or 1)))


def _izom_propui_free_layout_view_entry_uid(layout_item_uid):
    return f"entry:{str(layout_item_uid or '').strip()}"


def _izom_propui_free_layout_view_row_uid(row_index):
    return f"row:{max(1, int(row_index or 1))}"


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
