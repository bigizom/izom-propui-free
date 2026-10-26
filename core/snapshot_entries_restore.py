# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .snapshot_entries_normalize import (
    _izom_propui_free_normalize_entry_snapshot,
)
from .snapshot_entries_apply import (
    IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS,
    _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS,
    _izom_propui_free_apply_entry_snapshot,
    izom_propui_free_log_recovered,
)
from .collection_sync import (
    _izom_propui_free_collection_clear,
    _izom_propui_free_collection_order_matches,
    _izom_propui_free_sync_uid_collection,
)
from .entry_ids import _izom_propui_free_ensure_unique_snapshot_ids
from .snapshot_entries_common import _izom_propui_free_make_default_snapshot
from .snapshot_layout_common import _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS
from .snapshot_layout_ensure import (
    _izom_propui_free_sync_entry_layout_fields,
    izom_propui_free_ensure_layout_items,
)
from .snapshot_tree import (
    _IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS,
    _izom_propui_free_build_state_from_snapshots,
    _izom_propui_free_normalize_snapshot_display_rows,
)



def _izom_propui_free_restore_entries_full_inner(
    params,
    normalized,
    hierarchy_target_uid,
    *,
    layout_active_uid=None,
    normalize_layout=False,
    preserve_layout_items=False,
    ui_helpers=None,
):
    _izom_propui_free_collection_clear(params.izom_propui_free_entries)

    active_index = 0
    for index, snap in enumerate(normalized):
        item = params.izom_propui_free_entries.add()
        if ui_helpers is not None:
            ui_helpers._izom_propui_free_cache_entry_params(item, params)
        _izom_propui_free_apply_entry_snapshot(
            item,
            snap,
            assume_fresh=True,
        )
        if hierarchy_target_uid and snap['uid'] == hierarchy_target_uid:
            active_index = index

    final_index = min(active_index, max(0, len(params.izom_propui_free_entries) - 1))
    params.izom_propui_free_active_index = final_index
    try:
        params.izom_propui_free_active_uid = getattr(params.izom_propui_free_entries[final_index], 'uid', '') if params.izom_propui_free_entries else ''
        params.izom_propui_free_selected_uids_json = f'["{params.izom_propui_free_active_uid}"]' if params.izom_propui_free_active_uid else "[]"
        params.izom_propui_free_selection_anchor_uid = getattr(params, 'izom_propui_free_active_uid', '')
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    if preserve_layout_items:
        _izom_propui_free_sync_entry_layout_fields(params)
    else:
        izom_propui_free_ensure_layout_items(
            params,
            entry_snapshots=normalized,
            active_uid=layout_active_uid,
            normalize_layout=bool(normalize_layout),
        )


def _izom_propui_free_restore_entries_incremental_inner(
    params,
    normalized,
    hierarchy_target_uid,
    *,
    layout_active_uid=None,
    normalize_layout=False,
    preserve_layout_items=False,
    ui_helpers=None,
):
    collection = getattr(params, 'izom_propui_free_entries', None)
    if collection is None:
        return

    def _add_entry_item(target_collection):
        item = target_collection.add()
        if ui_helpers is not None:
            ui_helpers._izom_propui_free_cache_entry_params(item, params)
        return item

    def _sync_entry_item(item, snap):
        try:
            assume_fresh = not str(getattr(item, 'uid', '') or '').strip()
        except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
            assume_fresh = False
        _izom_propui_free_apply_entry_snapshot(
            item,
            snap,
            assume_fresh=assume_fresh,
        )

    _izom_propui_free_sync_uid_collection(
        collection,
        normalized,
        add_item=_add_entry_item,
        sync_item=_sync_entry_item,
    )

    active_index = 0
    for index, snap in enumerate(normalized):
        if hierarchy_target_uid and snap['uid'] == hierarchy_target_uid:
            active_index = index
            break

    final_index = min(active_index, max(0, len(collection) - 1))
    params.izom_propui_free_active_index = final_index
    try:
        params.izom_propui_free_active_uid = getattr(collection[final_index], 'uid', '') if collection else ''
        params.izom_propui_free_selected_uids_json = f'["{params.izom_propui_free_active_uid}"]' if params.izom_propui_free_active_uid else "[]"
        params.izom_propui_free_selection_anchor_uid = getattr(params, 'izom_propui_free_active_uid', '')
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    if preserve_layout_items:
        _izom_propui_free_sync_entry_layout_fields(params)
    else:
        izom_propui_free_ensure_layout_items(
            params,
            entry_snapshots=normalized,
            active_uid=layout_active_uid,
            normalize_layout=bool(normalize_layout),
        )


def izom_propui_free_restore_entries(params, snapshots, active_uid=None, layout_active_uid=None, normalize_layout=False, preserve_layout_items=False):
    snapshots = [dict(snap) for snap in (snapshots or [])]
    defaults = _izom_propui_free_make_default_snapshot(1)
    for snap in snapshots:
        for field_name in IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS:
            if field_name not in snap:
                snap[field_name] = defaults.get(field_name, '')
    state = _izom_propui_free_build_state_from_snapshots(snapshots)
    normalized = state['snapshots']

    _izom_propui_free_ensure_unique_snapshot_ids(normalized)

    for index, snap in enumerate(normalized, start=1):
        _izom_propui_free_normalize_entry_snapshot(index, snap, state)

    if normalize_layout:
        _izom_propui_free_normalize_snapshot_display_rows(normalized)

    def _resolve_target_uid(explicit_uid, uid_attr_name, index_attr_name, fallback_uid=''):
        if not normalized:
            return ''
        target_uid = str(explicit_uid or getattr(params, uid_attr_name, '') or '').strip()
        if target_uid:
            return target_uid
        try:
            index_hint = int(getattr(params, index_attr_name, 0))
        except _IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS:
            index_hint = 0
        index_hint = max(0, min(index_hint, len(normalized) - 1))
        target_uid = str(normalized[index_hint]['uid'] or '').strip()
        if target_uid:
            return target_uid
        return str(fallback_uid or normalized[0]['uid'] or '').strip()

    hierarchy_target_uid = _resolve_target_uid(active_uid, 'izom_propui_free_active_uid', 'izom_propui_free_active_index')
    ui_helpers = None
    entry_update_guard = None
    entry_runtime_update_guard = False
    value_label_update_guard = False
    try:
        from ..ui import helpers as _izom_propui_free_ui_helpers

        ui_helpers = _izom_propui_free_ui_helpers
        ui_helpers._izom_propui_free_clear_cached_entry_params(params)
        ui_helpers._izom_propui_free_suspend_list_context_updates(params)
        entry_update_guard = ui_helpers._izom_propui_free_suspend_entry_updates(params)
        ui_helpers._izom_propui_free_suspend_entry_runtime_update_callbacks()
        entry_runtime_update_guard = True
        ui_helpers._izom_propui_free_suspend_value_label_update_callbacks()
        value_label_update_guard = True
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS:
        ui_helpers = None

    try:
        try:
            try:
                current_entry_count = len(getattr(params, 'izom_propui_free_entries', []) or [])
            except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
                current_entry_count = 0
            if current_entry_count:
                _izom_propui_free_restore_entries_incremental_inner(
                    params,
                    normalized,
                    hierarchy_target_uid,
                    layout_active_uid=layout_active_uid,
                    normalize_layout=bool(normalize_layout),
                    preserve_layout_items=bool(preserve_layout_items),
                    ui_helpers=ui_helpers,
                )
                if not _izom_propui_free_collection_order_matches(params.izom_propui_free_entries, normalized):
                    raise RuntimeError("entry incremental restore order mismatch")
            else:
                _izom_propui_free_restore_entries_full_inner(
                    params,
                    normalized,
                    hierarchy_target_uid,
                    layout_active_uid=layout_active_uid,
                    normalize_layout=bool(normalize_layout),
                    preserve_layout_items=bool(preserve_layout_items),
                    ui_helpers=ui_helpers,
                )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
            )
            _izom_propui_free_restore_entries_full_inner(
                params,
                normalized,
                hierarchy_target_uid,
                layout_active_uid=layout_active_uid,
                normalize_layout=bool(normalize_layout),
                preserve_layout_items=bool(preserve_layout_items),
                ui_helpers=ui_helpers,
            )
    finally:
        if ui_helpers is not None:
            try:
                ui_helpers._izom_propui_free_cache_params_entries(params)
            finally:
                if value_label_update_guard:
                    ui_helpers._izom_propui_free_resume_value_label_update_callbacks(preserve_global_guards=True)
                if entry_runtime_update_guard:
                    ui_helpers._izom_propui_free_resume_entry_runtime_update_callbacks()
                if entry_update_guard is not None:
                    ui_helpers._izom_propui_free_resume_entry_updates(params)
                ui_helpers._izom_propui_free_resume_list_context_updates(params)

    try:
        from .cache import izom_propui_free_invalidate_params_cache

        izom_propui_free_invalidate_params_cache(params)
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
