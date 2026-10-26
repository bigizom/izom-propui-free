# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_entries_shared_copy import (
    _izom_propui_free_bump_collection_revision,
    _izom_propui_free_invalidate_entry_structure_cache,
    _izom_propui_free_resume_entry_updates,
    _izom_propui_free_suspend_entry_updates,
    izom_propui_free_log_recovered,
)
from ..core.snapshot_entries_restore import izom_propui_free_restore_entries
from .helper_selection_entries import _izom_propui_free_active_entry_uid


_IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_reorder_entry_collection_direct(
    params,
    ordered_uids,
    *,
    refresh_names=True,
    bump_revision=True,
):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    target_order = [
        str(uid or '').strip()
        for uid in (ordered_uids or ())
        if str(uid or '').strip()
    ]
    if collection is None or not target_order or len(target_order) != len(collection):
        return False

    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        index_by_uid = {}
        for index, item in enumerate(collection):
            uid = str(getattr(item, 'uid', '') or '').strip()
            if not uid or uid in index_by_uid:
                return False
            index_by_uid[uid] = index

        if set(index_by_uid) != set(target_order):
            return False

        order_changed = False
        for target_index, uid in enumerate(target_order):
            current_index = index_by_uid.get(uid)
            if current_index is None:
                return False
            if current_index == target_index:
                continue
            order_changed = True
            collection.move(current_index, target_index)
            low, high = sorted((target_index, current_index))
            for cursor in range(low, high + 1):
                item_uid = str(getattr(collection[cursor], 'uid', '') or '').strip()
                if item_uid:
                    index_by_uid[item_uid] = cursor

        izom_propui_free_entry_display_name = None
        if bool(refresh_names):
            try:
                from ..core.text import izom_propui_free_entry_display_name
            except ImportError as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                izom_propui_free_entry_display_name = None

        if order_changed or bool(refresh_names):
            for index, item in enumerate(collection, start=1):
                try:
                    if getattr(item, 'ui_order', None) != index:
                        item.ui_order = index
                    if izom_propui_free_entry_display_name is not None:
                        item.name = izom_propui_free_entry_display_name(item, fallback_index=index)
                except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    if bool(bump_revision):
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
        _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_apply_entry_structure_snapshots_direct(
    params,
    snapshots,
    *,
    field_names=None,
    field_update_uids=None,
):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    if collection is None:
        return False
    target_order = [
        str((snap or {}).get('uid', '') or '').strip()
        for snap in (snapshots or ())
        if str((snap or {}).get('uid', '') or '').strip()
    ]
    if not _izom_propui_free_reorder_entry_collection_direct(
        params,
        target_order,
        refresh_names=False,
        bump_revision=False,
    ):
        return False

    fields = tuple(field_names or ('parent_uid',))
    update_uid_set = None
    if field_update_uids is not None:
        update_uid_set = {
            str(uid or '').strip()
            for uid in (field_update_uids or ())
            if str(uid or '').strip()
        }
        if not update_uid_set:
            _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
            _izom_propui_free_invalidate_entry_structure_cache(params)
            return True
    snap_by_uid = {}
    for snap in (snapshots or ()):
        uid = str((snap or {}).get('uid', '') or '').strip()
        if not uid:
            continue
        if update_uid_set is not None and uid not in update_uid_set:
            continue
        snap_by_uid[uid] = snap
    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        for item in collection:
            uid = str(getattr(item, 'uid', '') or '').strip()
            if update_uid_set is not None and uid not in update_uid_set:
                continue
            snap = snap_by_uid.get(uid)
            if snap is None:
                return False
            for field_name in fields:
                if field_name not in snap:
                    continue
                try:
                    new_value = str(snap.get(field_name, '') or '').strip() if field_name == 'parent_uid' else snap.get(field_name)
                    if getattr(item, field_name, None) != new_value:
                        setattr(item, field_name, new_value)
                except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
                    return False
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_update_entry_structure_fields_direct(params, field_values_by_uid):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    normalized_updates = {}
    for uid, field_values in (field_values_by_uid or {}).items():
        uid = str(uid or '').strip()
        if not uid or not isinstance(field_values, dict):
            continue
        normalized_updates[uid] = dict(field_values)
    if collection is None or not normalized_updates:
        return False

    remaining_uids = set(normalized_updates)
    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        for item in collection:
            uid = str(getattr(item, 'uid', '') or '').strip()
            if uid not in remaining_uids:
                continue
            for field_name, new_value in normalized_updates.get(uid, {}).items():
                try:
                    if field_name == 'parent_uid':
                        new_value = str(new_value or '').strip()
                    if getattr(item, field_name, None) != new_value:
                        setattr(item, field_name, new_value)
                except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
                    return False
            remaining_uids.discard(uid)
            if not remaining_uids:
                break
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    if remaining_uids:
        return False
    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_move_entry_block_and_update_fields_direct(
    params,
    start_index,
    block_len,
    insert_index,
    *,
    field_values_by_uid=None,
):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    try:
        start_index = int(start_index)
        block_len = int(block_len)
        insert_index = int(insert_index)
    except (TypeError, ValueError):
        return False
    if (
        collection is None
        or not hasattr(collection, 'move')
        or block_len <= 0
        or start_index < 0
        or start_index + block_len > len(collection)
        or insert_index < 0
        or insert_index > len(collection) - block_len
    ):
        return False

    normalized_updates = {}
    for uid, field_values in (field_values_by_uid or {}).items():
        uid = str(uid or '').strip()
        if uid and isinstance(field_values, dict):
            normalized_updates[uid] = dict(field_values)

    collection_len = len(collection)
    affected_start = min(start_index, insert_index)
    affected_end = max(start_index + block_len, insert_index + block_len)

    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        if insert_index != start_index:
            if insert_index > start_index:
                target_end = insert_index + block_len
                for _offset in range(block_len):
                    collection.move(start_index, target_end - 1)
            else:
                for offset in range(block_len):
                    collection.move(start_index + offset, insert_index + offset)

        remaining_uids = set(normalized_updates)
        affected_start = max(0, min(affected_start, collection_len))
        affected_end = max(affected_start, min(affected_end, collection_len))
        for zero_index in range(affected_start, affected_end):
            item = collection[zero_index]
            index = zero_index + 1
            try:
                if getattr(item, 'ui_order', None) != index:
                    item.ui_order = index
            except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                return False
            uid = str(getattr(item, 'uid', '') or '').strip()
            if uid not in remaining_uids:
                continue
            for field_name, new_value in normalized_updates.get(uid, {}).items():
                try:
                    if field_name == 'parent_uid':
                        new_value = str(new_value or '').strip()
                    if getattr(item, field_name, None) != new_value:
                        setattr(item, field_name, new_value)
                except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
                    return False
            remaining_uids.discard(uid)
        if remaining_uids:
            for zero_index, item in enumerate(collection):
                if affected_start <= zero_index < affected_end:
                    continue
                uid = str(getattr(item, 'uid', '') or '').strip()
                if uid not in remaining_uids:
                    continue
                for field_name, new_value in normalized_updates.get(uid, {}).items():
                    try:
                        if field_name == 'parent_uid':
                            new_value = str(new_value or '').strip()
                        if getattr(item, field_name, None) != new_value:
                            setattr(item, field_name, new_value)
                    except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                        izom_propui_free_log_recovered(
                            category='UI',
                            exception=exc,
                        )
                        return False
                remaining_uids.discard(uid)
                if not remaining_uids:
                    break
        if remaining_uids:
            return False
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_remove_entry_uids_direct(params, removed_uids, *, parent_updates=None):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    normalized_removed_uids = {
        str(uid or '').strip()
        for uid in (removed_uids or ())
        if str(uid or '').strip()
    }
    if collection is None or not normalized_removed_uids:
        return False

    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        index_by_uid = {}
        for index, item in enumerate(collection):
            uid = str(getattr(item, 'uid', '') or '').strip()
            if uid:
                index_by_uid[uid] = index

        for child_uid, parent_uid in (parent_updates or {}).items():
            child_uid = str(child_uid or '').strip()
            child_index = index_by_uid.get(child_uid)
            if child_index is None:
                continue
            try:
                collection[child_index].parent_uid = str(parent_uid or '').strip()
            except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                continue

        remove_indices = sorted(
            {
                index_by_uid[uid]
                for uid in normalized_removed_uids
                if uid in index_by_uid
            },
            reverse=True,
        )
        if not remove_indices:
            return False
        for index in remove_indices:
            collection.remove(index)
        try:
            params.izom_propui_free_active_index = min(
                max(0, int(getattr(params, 'izom_propui_free_active_index', 0) or 0)),
                max(0, len(collection) - 1),
            )
        except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_remove_single_entry_index_direct(params, uid, index):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    uid = str(uid or '').strip()
    try:
        index = int(index)
    except (TypeError, ValueError):
        return False
    if collection is None or not uid or not (0 <= index < len(collection)):
        return False
    if str(getattr(collection[index], 'uid', '') or '').strip() != uid:
        return False

    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        collection.remove(index)
        try:
            params.izom_propui_free_active_index = min(
                max(0, int(getattr(params, 'izom_propui_free_active_index', 0) or 0)),
                max(0, len(collection) - 1),
            )
        except _IZOM_PROPUI_FREE_ENTRY_STRUCTURE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)

    _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_entries')
    _izom_propui_free_invalidate_entry_structure_cache(params)
    return True


def _izom_propui_free_restore_with_editor_focus(params, snapshots, *, focus_context='HIERARCHY', focus_uid='', preserve_layout_items=False):
    hierarchy_active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
    layout_active_uid = str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
    if str(focus_context or 'HIERARCHY').strip().upper() == 'LAYOUT':
        if focus_uid:
            layout_active_uid = focus_uid
    else:
        if focus_uid:
            hierarchy_active_uid = focus_uid
    izom_propui_free_restore_entries(
        params,
        snapshots,
        active_uid=hierarchy_active_uid,
        layout_active_uid=layout_active_uid,
        preserve_layout_items=bool(preserve_layout_items),
    )

def _izom_propui_free_restore_entries_preserving_layout(params, snapshots, *, focus_context='HIERARCHY', focus_uid=''):
    _izom_propui_free_restore_with_editor_focus(
        params,
        snapshots,
        focus_context=focus_context,
        focus_uid=focus_uid,
        preserve_layout_items=True,
    )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
