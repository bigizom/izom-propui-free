# SPDX-License-Identifier: GPL-3.0-or-later

from .snapshot_layout_restore_items import (
    _izom_propui_free_restore_layout_items,
)
from .snapshot_layout_common import (
    _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS,
    _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS,
    _izom_propui_free_layout_row_field_values,
    izom_propui_free_log_recovered,
)
from .snapshot_layout_common import izom_propui_free_snapshot_layout_items
from .snapshot_layout_normalize import (
    _izom_propui_free_normalize_layout_snapshots,
)



def _izom_propui_free_sync_entry_layout_fields(params, layout_snapshots=None):
    layout_snapshots = list(layout_snapshots if layout_snapshots is not None else izom_propui_free_snapshot_layout_items(params))
    entries = list(getattr(params, 'izom_propui_free_entries', []) or [])
    entry_by_uid = {
        str(getattr(entry, 'uid', '') or '').strip(): entry
        for entry in entries
        if str(getattr(entry, 'uid', '') or '').strip()
    }
    guard = None
    try:
        from ..ui.helper_cache_updates_common import _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD

        guard = _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS:
        guard = None

    synced_entry_uids = set()
    for snap in layout_snapshots:
        entry_uid = str(snap['entry_uid'] or '').strip()
        if not entry_uid or entry_uid in synced_entry_uids:
            continue
        entry = entry_by_uid.get(entry_uid)
        if entry is None:
            continue
        synced_entry_uids.add(entry_uid)
        try:
            display_order = max(1, int(snap['row_index'] or 1))
            row_slot = max(1, int(snap['column_index'] or 1))
            if (
                int(getattr(entry, 'display_order', 1) or 1) == display_order
                and int(getattr(entry, 'row_slot', 1) or 1) == row_slot
            ):
                continue
            guard_key = str(getattr(entry, 'uid', '') or '').strip()
            if not guard_key:
                pointer = getattr(entry, 'as_pointer', None)
                guard_key = str(pointer()) if callable(pointer) else str(id(entry))
            if guard is not None:
                guard.add(guard_key)
            try:
                entry.display_order = display_order
                entry.row_slot = row_slot
            finally:
                if guard is not None:
                    guard.discard(guard_key)
        except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
            )

def izom_propui_free_ensure_layout_items(params, entry_snapshots=None, active_uid=None, normalize_layout=False):
    if not hasattr(params, 'izom_propui_free_layout_items'):
        return []

    from .snapshot_entries import izom_propui_free_snapshot_entries

    entry_snapshots = list(entry_snapshots if entry_snapshots is not None else izom_propui_free_snapshot_entries(params))
    entry_uids = [
        str(snap['uid'] or '').strip()
        for snap in entry_snapshots
        if str(snap['uid'] or '').strip()
    ]
    entry_uid_set = set(entry_uids)
    existing = []
    seen_layout_uids = set()
    for order_index, snap in enumerate(izom_propui_free_snapshot_layout_items(params)):
        layout_uid = str(snap['uid'] or '').strip()
        entry_uid = str(snap['entry_uid'] or '').strip()
        if not entry_uid or entry_uid not in entry_uid_set:
            continue
        if layout_uid in seen_layout_uids:
            continue
        seen_layout_uids.add(layout_uid)
        existing.append({
            'uid': layout_uid,
            'entry_uid': entry_uid,
            'row_index': max(1, int(snap['row_index'] or 1)),
            'column_index': max(1, int(snap['column_index'] or 1)),
            **_izom_propui_free_layout_row_field_values(snap),
            '_order': order_index,
        })

    # The Generated Layout is intentionally user-authored. Do NOT bootstrap
    # layout items from the entry list when it's empty — that path used to
    # auto-populate rows (sometimes shared, sometimes not) the moment any
    # consumer asked for a layout view, which surprised users on Generate.

    if normalize_layout:
        existing = _izom_propui_free_normalize_layout_snapshots(existing)
    else:
        existing.sort(
            key=lambda item: (
                int(item['row_index'] or 1),
                int(item['column_index'] or 1),
                int(item.get('_order', 0) or 0),
            )
        )
    for snap in existing:
        snap.pop('_order', None)

    restored = _izom_propui_free_restore_layout_items(params, existing, active_uid=active_uid)
    _izom_propui_free_sync_entry_layout_fields(params, restored)

    try:
        from .cache import izom_propui_free_invalidate_params_cache

        izom_propui_free_invalidate_params_cache(params)
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
    try:
        from ..ui import helpers as _izom_propui_free_ui_helpers

        _izom_propui_free_ui_helpers._izom_propui_free_cache_params_entries(params)
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
    return restored


def _izom_propui_free_layout_view_entry_uid(layout_uid):
    return f"ENTRY_ITEM:{str(layout_uid or '').strip()}"


def _izom_propui_free_layout_view_row_uid(row_member_uids):
    # Canonical layout-view row id: keyed by the row's first member uid.
    members = [str(uid or '').strip() for uid in (row_member_uids or []) if str(uid or '').strip()]
    return f"ROW_HEADER:{members[0]}" if members else "ROW_HEADER:"

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
