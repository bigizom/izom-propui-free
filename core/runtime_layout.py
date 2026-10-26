# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .runtime_entries import (
    izom_propui_free_log_recovered,
    izom_propui_free_runtime_entries,
)
from .constants_display import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
)
from .snapshot_layout_common import (
    izom_propui_free_snapshot_layout_items,
)



def _izom_propui_free_runtime_facade_attr(name, fallback):
    try:
        from . import runtime as runtime_facade

        return getattr(runtime_facade, name, fallback)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(category='Core', exception=exc)
        return fallback


def _izom_propui_free_runtime_layout_entries_from_state(runtime_entries, layout_snapshots):
    entry_by_uid = {
        str(entry.get('uid', '') or '').strip(): entry
        for entry in runtime_entries
        if str(entry.get('uid', '') or '').strip()
    }

    ordered = []
    for layout_index, snap in enumerate(layout_snapshots, start=1):
        entry_uid = str(snap.get('entry_uid', '') or '').strip()
        entry = entry_by_uid.get(entry_uid)
        if entry is None:
            continue
        item = dict(entry)
        item['layout_uid'] = str(snap.get('uid', '') or '').strip()
        item['container_uid'] = ''
        item['display_order'] = max(1, int(snap.get('row_index', 1) or 1))
        item['row_slot'] = max(1, int(snap.get('column_index', 1) or 1))
        item['row_height_scale'] = snap.get('row_height_scale', IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT)
        item['row_inset_left_enabled'] = bool(snap.get('row_inset_left_enabled', False))
        item['row_inset_left_amount'] = snap.get('row_inset_left_amount', IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT)
        item['layout_index'] = layout_index
        ordered.append(item)
    return ordered


def izom_propui_free_runtime_layout_entries(params):
    runtime_entries_fn = _izom_propui_free_runtime_facade_attr(
        'izom_propui_free_runtime_entries',
        izom_propui_free_runtime_entries,
    )
    snapshot_layout_items_fn = _izom_propui_free_runtime_facade_attr(
        'izom_propui_free_snapshot_layout_items',
        izom_propui_free_snapshot_layout_items,
    )
    if params is not None:
        try:
            from .cache import (
                _izom_propui_free_cached_params_field,
            )

            return _izom_propui_free_cached_params_field(
                params,
                'runtime_layout_entries',
                lambda: _izom_propui_free_runtime_layout_entries_from_state(
                    runtime_entries_fn(params),
                    _izom_propui_free_cached_params_field(
                        params,
                        'layout_snapshots',
                        lambda: snapshot_layout_items_fn(params),
                    ),
                ),
            )
        except ImportError:
            pass
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(category='Core', exception=exc)
            pass

    runtime_entries = runtime_entries_fn(params)
    layout_snapshots = snapshot_layout_items_fn(params)
    return _izom_propui_free_runtime_layout_entries_from_state(runtime_entries, layout_snapshots)

def _izom_propui_free_runtime_display_groups(entries, cond_by_uid=None):
    cond_by_uid = cond_by_uid or {}
    filtered = []

    for entry in entries or []:
        prop_type = str(entry.get('prop_type', '') or '').strip().upper()
        if prop_type != 'TEXT':
            prop_id = str(entry.get('prop_id', '') or '').strip()
            if not prop_id:
                continue
        filtered.append((entry, int(entry.get('tree_index', 0) or 0), cond_by_uid.get(entry.get('uid'))))

    filtered.sort(
        key=lambda item: (
            int(item[0].get('display_order', item[0].get('ui_order', item[1] or 1)) or item[0].get('ui_order', item[1] or 1) or (item[1] or 1)),
            int(item[0].get('row_slot', 1) or 1),
            item[1],
        )
    )

    groups = []
    current_order = None
    for item in filtered:
        display_order = int(item[0].get('display_order', item[0].get('ui_order', item[1] or 1)) or item[0].get('ui_order', item[1] or 1) or (item[1] or 1))
        if current_order != display_order:
            groups.append([])
            current_order = display_order
        groups[-1].append(item)
    return groups

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
