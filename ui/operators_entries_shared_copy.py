# SPDX-License-Identifier: GPL-3.0-or-later


_IZOM_PROPUI_FREE_ENTRY_COPY_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_copy_snapshot_value(value):
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return tuple(value)
    return value


def _izom_propui_free_copy_snapshot_block(block):
    copied = [
        _izom_propui_free_copy_snapshot_value(snap)
        for snap in (block or ())
        if isinstance(snap, dict)
    ]
    uid_map = {}
    for snap in copied:
        old_uid = str(snap.get('uid', '') or '').strip()
        new_uid = _izom_propui_free_new_uid()
        uid_map[old_uid] = new_uid
        snap['uid'] = new_uid
    for snap in copied:
        parent_uid = str(snap.get('parent_uid', '') or '').strip()
        if parent_uid in uid_map:
            snap['parent_uid'] = uid_map[parent_uid]
    return copied


def _izom_propui_free_assign_duplicate_prop_ids(blocks, snapshots):
    excluded_types = {'TEXT'}
    existing_ids = set()
    for snap in snapshots or ():
        prop_type = str((snap or {}).get('prop_type', '') or '').strip().upper()
        if prop_type in excluded_types:
            continue
        prop_id = str((snap or {}).get('prop_id', '') or '').strip()
        if prop_id:
            existing_ids.add(prop_id)
    for block in blocks or []:
        for snap in block or []:
            if str((snap or {}).get('prop_type', '') or '').strip().upper() in excluded_types:
                continue
            raw_prop_id = str((snap or {}).get('prop_id', '') or '').strip() or 'prop'
            unique_prop_id = _izom_propui_free_unique_prop_id(raw_prop_id, existing_ids)
            snap['prop_id'] = unique_prop_id
            existing_ids.add(unique_prop_id)

def _izom_propui_free_set_entry_selection_direct(params, uid, index):
    uid = str(uid or '').strip()
    selected_json = f'["{uid}"]' if uid else "[]"
    try:
        active_index = max(0, int(index))
    except (TypeError, ValueError):
        active_index = 0

    guard_key = _izom_propui_free_suspend_entry_updates(params)
    try:
        try:
            params.izom_propui_free_active_index = active_index
            params.izom_propui_free_active_uid = uid
            params.izom_propui_free_selected_uids_json = selected_json
            params.izom_propui_free_selection_anchor_uid = uid
        except _IZOM_PROPUI_FREE_ENTRY_COPY_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_entry_updates(params)

    entry = None
    if uid:
        entries = getattr(params, 'izom_propui_free_entries', None) or []
        if 0 <= active_index < len(entries):
            candidate = entries[active_index]
            if str(getattr(candidate, 'uid', '') or '').strip() == uid:
                entry = candidate
    _izom_propui_free_smart_expand_selected_entry_sections_for_entry(params, entry, uid)


def _izom_propui_free_insert_entry_snapshot_direct(params, snap, insert_index):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    if collection is None:
        return False

    try:
        target_index = max(0, min(int(insert_index), len(collection)))
    except (TypeError, ValueError):
        target_index = len(collection)

    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    _izom_propui_free_suspend_entry_runtime_update_callbacks()
    _izom_propui_free_suspend_value_label_update_callbacks()
    item = None
    try:
        item = collection.add()
        _izom_propui_free_cache_entry_params(item, params)
        _izom_propui_free_apply_entry_snapshot(
            item,
            snap,
            assume_fresh=True,
        )
        current_index = len(collection) - 1
        if target_index != current_index:
            collection.move(current_index, target_index)
        _izom_propui_free_set_entry_selection_direct(params, snap.get('uid', ''), target_index)
    except _IZOM_PROPUI_FREE_ENTRY_COPY_ACCESS_ERRORS as exc:
        izom_propui_free_log_debug(
            "Could not insert entry snapshot; rolling back partial entry",
            category='UI',
            exception=exc,
        )
        if item is not None:
            try:
                collection.remove(len(collection) - 1)
            except _IZOM_PROPUI_FREE_ENTRY_COPY_ACCESS_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
        )
        return False
    finally:
        _izom_propui_free_resume_value_label_update_callbacks(preserve_global_guards=True)
        _izom_propui_free_resume_entry_runtime_update_callbacks()
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_insert_entry_snapshot_block_direct(params, block, insert_index):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    snapshots = [dict(snap) for snap in (block or []) if str((snap or {}).get('uid', '') or '').strip()]
    if collection is None or not snapshots:
        return False

    try:
        target_index = max(0, min(int(insert_index), len(collection)))
    except (TypeError, ValueError):
        target_index = len(collection)

    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    _izom_propui_free_suspend_entry_runtime_update_callbacks()
    _izom_propui_free_suspend_value_label_update_callbacks()
    added_count = 0
    try:
        for snap in snapshots:
            item = collection.add()
            added_count += 1
            _izom_propui_free_cache_entry_params(item, params)
            _izom_propui_free_apply_entry_snapshot(
                item,
                snap,
                assume_fresh=True,
            )

        for _index in range(added_count):
            collection.move(len(collection) - 1, target_index)
    except _IZOM_PROPUI_FREE_ENTRY_COPY_ACCESS_ERRORS as exc:
        izom_propui_free_log_debug(
            "Could not insert entry snapshot block; rolling back partial entries",
            category='UI',
            exception=exc,
        )
        for _index in range(added_count):
            try:
                collection.remove(len(collection) - 1)
            except _IZOM_PROPUI_FREE_ENTRY_COPY_ACCESS_ERRORS as remove_exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=remove_exc,
                )
                break
        return False
    finally:
        _izom_propui_free_resume_value_label_update_callbacks(preserve_global_guards=True)
        _izom_propui_free_resume_entry_runtime_update_callbacks()
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401
from ..core.diagnostics import (
    izom_propui_free_log_debug,
    izom_propui_free_log_recovered,
)
from ..core.entry_ids import (
    _izom_propui_free_new_uid,
    _izom_propui_free_unique_prop_id,
)
from .helper_cache_updates_entry_params import (
    _izom_propui_free_cache_entry_params,
    _izom_propui_free_resume_entry_runtime_update_callbacks,
    _izom_propui_free_resume_entry_updates,
    _izom_propui_free_suspend_entry_runtime_update_callbacks,
    _izom_propui_free_suspend_entry_updates,
)
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_entry_structure_cache
from .helper_cache_updates_session import (
    _izom_propui_free_resume_value_label_update_callbacks,
    _izom_propui_free_suspend_value_label_update_callbacks,
)
from .helper_selection_collections import _izom_propui_free_bump_collection_revision
from .helper_selection_common import _izom_propui_free_smart_expand_selected_entry_sections_for_entry
from ..core.snapshot_entries_apply import _izom_propui_free_apply_entry_snapshot


__all__ = izom_propui_free_public_names(globals())
