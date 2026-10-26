# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_layout_live_core import (
    izom_propui_free_log_recovered,
)
from ..core.snapshot_layout_ensure import (
    _izom_propui_free_layout_view_entry_uid,
    _izom_propui_free_sync_entry_layout_fields,
)
from ..core.snapshot_layout_normalize import (
    _izom_propui_free_order_layout_rows_by_container,
)
from ..core.snapshot_layout_restore_items import _izom_propui_free_restore_layout_items
from .helper_layout_rows import _izom_propui_free_ordered_layout_snapshots
from .operators_layout_view import _izom_propui_free_rebuild_layout_view_items



def _izom_propui_free_restore_layout_snapshots(
    params,
    layout_snapshots,
    *,
    active_layout_uid='',
    layout_snapshots_are_ordered=False,
    sync_view_selection=True,
):
    ordered_snapshots = (
        list(layout_snapshots or [])
        if bool(layout_snapshots_are_ordered)
        else _izom_propui_free_order_layout_rows_by_container(
            _izom_propui_free_ordered_layout_snapshots(layout_snapshots),
            layout_snapshots_are_ordered=True,
        )
    )
    _izom_propui_free_restore_layout_items(
        params,
        ordered_snapshots,
        active_uid=active_layout_uid,
        rebuild_view=False,
        return_snapshots=False,
        assume_canonical=True,
    )
    _izom_propui_free_sync_entry_layout_fields(params, ordered_snapshots)
    _izom_propui_free_rebuild_layout_view_items(
        params,
        preferred_active_uid=_izom_propui_free_layout_view_entry_uid(active_layout_uid) if active_layout_uid else '',
        layout_snapshots=ordered_snapshots,
        layout_snapshots_are_ordered=True,
        sync_selection=sync_view_selection,
    )
    try:
        from ..core.cache import izom_propui_free_invalidate_params_cache

        izom_propui_free_invalidate_params_cache(params)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
