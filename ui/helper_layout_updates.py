# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .helper_layout_view import (
    izom_propui_free_log_recovered,
    izom_propui_free_snapshot_layout_items,
)
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD
from .helper_cache_updates_entry_params import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_find_params_for_entry,
)
from .helper_cache_updates_entry_runtime import _izom_propui_free_entry_runtime_state_updated
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_layout_cache
from .helper_layout_lookup import (
    _izom_propui_free_find_params_for_layout_item,
    _izom_propui_free_find_params_for_layout_row,
    _izom_propui_free_layout_item_by_entry_uid,
)
from .helper_layout_rows import _izom_propui_free_row_slot_value
from .helper_layout_selection import _izom_propui_free_active_layout_item
from .helper_selection_context import _izom_propui_free_list_context_updates_suspended
from ..core.constants import IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT



def _izom_propui_free_update_logical_row_field(entry, *, display_order=None, row_slot=None):
    from .operators_layout_support import (
        _izom_propui_free_reinsert_layout_item_at_row,
        _izom_propui_free_reposition_layout_item_column,
        _izom_propui_free_restore_layout_snapshots,
    )

    guard_key = getattr(entry, 'uid', '') or str(entry.as_pointer())
    if guard_key in _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD:
        return

    params = _izom_propui_free_find_params_for_entry(entry, None)
    if not params:
        return
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return

    layout_snapshots = izom_propui_free_snapshot_layout_items(params)
    if not layout_snapshots:
        return

    entry_uid = str(getattr(entry, 'uid', '') or '')
    active_layout_item = _izom_propui_free_active_layout_item(params)
    if active_layout_item is not None and str(getattr(active_layout_item, 'entry_uid', '') or '').strip() == entry_uid:
        layout_item = active_layout_item
    else:
        layout_item = _izom_propui_free_layout_item_by_entry_uid(params, entry_uid)
    layout_uid = str(getattr(layout_item, 'uid', '') or '').strip() if layout_item is not None else ''
    if not layout_uid:
        return

    changed = False
    if display_order is not None:
        changed = _izom_propui_free_reinsert_layout_item_at_row(layout_snapshots, layout_uid, display_order, params=params)
    elif row_slot is not None:
        changed = _izom_propui_free_reposition_layout_item_column(layout_snapshots, layout_uid, row_slot, params=params)

    if not changed:
        return

    _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.add(guard_key)
    try:
        _izom_propui_free_restore_layout_snapshots(
            params,
            layout_snapshots,
            active_layout_uid=layout_uid,
        )
    finally:
        _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_row_slot_updated(entry, _context):
    guard_key = getattr(entry, 'uid', '') or str(entry.as_pointer())
    if guard_key in _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD:
        return
    params = _izom_propui_free_find_params_for_entry(entry, None)
    if params is not None and _izom_propui_free_list_context_updates_suspended(params):
        return
    _izom_propui_free_update_logical_row_field(entry, row_slot=_izom_propui_free_row_slot_value(entry))
    _izom_propui_free_entry_runtime_state_updated(entry, None)


def _izom_propui_free_layout_row_settings_updated(layout_row, context):
    guard_key = ''
    try:
        guard_key = str(layout_row.as_pointer())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    if guard_key and guard_key in _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD:
        return
    params = _izom_propui_free_find_params_for_layout_row(layout_row, context)
    if params is not None:
        if _izom_propui_free_list_context_updates_suspended(params):
            return
        if bool(getattr(layout_row, 'row_inset_left_enabled', False)):
            try:
                if float(getattr(layout_row, 'row_inset_left_amount', 0.0) or 0.0) != float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT):
                    layout_row.row_inset_left_amount = IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
        _izom_propui_free_invalidate_layout_cache(params)


def _izom_propui_free_layout_column_width_updated(layout_item, _context):
    guard_key = str(getattr(layout_item, 'uid', '') or '').strip()
    if not guard_key:
        try:
            guard_key = str(layout_item.as_pointer())
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            guard_key = ''
    if guard_key and guard_key in _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD:
        return
    params = _izom_propui_free_find_params_for_layout_item(layout_item, None)
    if params is None:
        return
    if _izom_propui_free_bulk_entry_updates_suspended(params) or _izom_propui_free_list_context_updates_suspended(params):
        return
    _izom_propui_free_invalidate_layout_cache(params)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
