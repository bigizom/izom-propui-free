# SPDX-License-Identifier: GPL-3.0-or-later

from .snapshot_entries_runtime import (
    izom_propui_free_snapshot_entries,
)
from .snapshot_entries_restore import (
    _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS,
    _izom_propui_free_ensure_unique_snapshot_ids,
    izom_propui_free_log_recovered,
    izom_propui_free_restore_entries,
)
from .entry_ids import _izom_propui_free_limit_entry_snapshot_strings



def _izom_propui_free_active_uid(params):
    if not params.izom_propui_free_entries:
        return None
    index = max(0, min(params.izom_propui_free_active_index, len(params.izom_propui_free_entries) - 1))
    return getattr(params.izom_propui_free_entries[index], 'uid', None)


def izom_propui_free_ensure_consistency(params):
    snapshots = izom_propui_free_snapshot_entries(params)
    for snap in snapshots:
        _izom_propui_free_limit_entry_snapshot_strings(snap)
    renames = _izom_propui_free_ensure_unique_snapshot_ids(snapshots)
    izom_propui_free_restore_entries(
        params,
        snapshots,
        active_uid=_izom_propui_free_active_uid(params),
        layout_active_uid=str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip(),
        normalize_layout=True,
    )
    try:
        from .cache import izom_propui_free_invalidate_params_cache

        izom_propui_free_invalidate_params_cache(params)
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
    return renames

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
