# SPDX-License-Identifier: GPL-3.0-or-later


from .helpers import (
    _izom_propui_free_active_layout_view_item,
)
from .operators_layout_mutation import (
    _izom_propui_free_apply_layout_rows_to_items,
    _izom_propui_free_layout_item_position,
    _izom_propui_free_layout_rows_from_items,
    _izom_propui_free_layout_view_entry_uid,
)
from ..core.cache_common import izom_propui_free_invalidate_params_cache_fields
from ..core.snapshot_layout_common import _izom_propui_free_make_default_layout_snapshot
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD
from .helper_layout_common import _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE
from .helper_selection_collections import _izom_propui_free_bump_collection_revision
from .helper_selection_context import (
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
)
from .operators_layout_base import (
    _izom_propui_free_make_fast_ordered_layout_snapshot,
)
from .operators_layout_live_core import _izom_propui_free_collection_item_and_index_by_uid



def _izom_propui_free_gl_auto_sync_enabled(params):
    return False

def _izom_propui_free_gl_safe_import_enabled(params):
    return bool(getattr(params, 'izom_propui_free_gl_safe_import', True))

def _izom_propui_free_gl_add_into_active_row_enabled(params):
    return False

def _izom_propui_free_layout_entry_uid_set(layout_snapshots):
    return {
        str(snap.get('entry_uid', '') or '').strip()
        for snap in (layout_snapshots or [])
        if str(snap.get('entry_uid', '') or '').strip()
    }

def _izom_propui_free_append_layout_single_rows_direct(layout_snapshots, entry_uids, *, after_layout_uid=''):
    target_entry_uids = [
        str(entry_uid or '').strip()
        for entry_uid in (entry_uids or ())
        if str(entry_uid or '').strip()
    ]
    if not target_entry_uids:
        return []

    target_layout_uid = str(after_layout_uid or '').strip()
    if not target_layout_uid:
        return []

    target_snapshot = None
    for snap in layout_snapshots or ():
        if str(snap.get('uid', '') or '').strip() == target_layout_uid:
            target_snapshot = snap
            break
    if target_snapshot is None:
        return []

    try:
        insert_after_row = max(1, int(target_snapshot.get('row_index', 1) or 1))
    except (TypeError, ValueError):
        return []

    inserted_snapshots = []
    for offset, entry_uid in enumerate(target_entry_uids, start=1):
        snap = _izom_propui_free_make_default_layout_snapshot(len(layout_snapshots) + offset, entry_uid=entry_uid)
        snap['row_index'] = insert_after_row + offset
        snap['column_index'] = 1
        inserted_snapshots.append(snap)

    insert_count = len(inserted_snapshots)
    next_snapshots = []
    inserted = False
    for source in layout_snapshots or ():
        try:
            source_row = max(1, int(source.get('row_index', 1) or 1))
        except (TypeError, ValueError):
            source_row = 1
        if not inserted and source_row > insert_after_row:
            next_snapshots.extend(inserted_snapshots)
            inserted = True
        if source_row > insert_after_row:
            source['row_index'] = source_row + insert_count
        next_snapshots.append(source)
    if not inserted:
        next_snapshots.extend(inserted_snapshots)

    layout_snapshots[:] = next_snapshots
    return inserted_snapshots

def _izom_propui_free_append_layout_entry_live_single_row(params, entry_uid, *, after_layout_uid=''):
    if params is None:
        return ''
    target_entry_uid = str(entry_uid or '').strip()
    target_layout_uid = str(after_layout_uid or '').strip()
    if not target_entry_uid or not target_layout_uid:
        return ''

    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    row_collection = getattr(params, 'izom_propui_free_layout_rows', None)
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if layout_collection is None or row_collection is None or view_collection is None:
        return ''

    target_item, _target_index = _izom_propui_free_collection_item_and_index_by_uid(layout_collection, target_layout_uid)
    target_view_item, target_view_index = _izom_propui_free_collection_item_and_index_by_uid(
        view_collection,
        _izom_propui_free_layout_view_entry_uid(target_layout_uid),
    )
    if target_item is None or target_view_item is None or target_view_index < 0:
        return ''

    try:
        target_row = max(1, int(getattr(target_item, 'row_index', 1) or 1))
    except (TypeError, ValueError):
        return ''
    insert_index = len(layout_collection)
    for index, item in enumerate(layout_collection):
        try:
            row_index = max(1, int(getattr(item, 'row_index', 1) or 1))
        except (TypeError, ValueError):
            row_index = 1
        if row_index > target_row:
            insert_index = index
            break

    snap = _izom_propui_free_make_default_layout_snapshot(len(layout_collection) + 1, entry_uid=target_entry_uid)
    snap['row_index'] = target_row + 1
    snap['column_index'] = 1
    new_layout_uid = str(snap.get('uid', '') or '').strip()
    if not new_layout_uid:
        return ''

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        for item in layout_collection:
            try:
                row_index = max(1, int(getattr(item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if row_index > target_row:
                item.row_index = row_index + 1

        for row_item in row_collection:
            try:
                row_index = max(1, int(getattr(row_item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if row_index > target_row:
                row_item.row_index = row_index + 1

        layout_item = layout_collection.add()
        layout_item.uid = new_layout_uid
        _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.add(new_layout_uid)
        try:
            layout_item.entry_uid = target_entry_uid
            layout_item.row_index = target_row + 1
            layout_item.column_index = 1
        finally:
            _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD.discard(new_layout_uid)
        if insert_index < len(layout_collection) - 1:
            layout_collection.move(len(layout_collection) - 1, insert_index)

        row_item = row_collection.add()
        row_item.row_index = target_row + 1
        row_insert_index = len(row_collection) - 1
        for index, existing_row_item in enumerate(row_collection):
            if index == len(row_collection) - 1:
                continue
            try:
                row_index = max(1, int(getattr(existing_row_item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if row_index > target_row + 1:
                row_insert_index = index
                break
        if row_insert_index < len(row_collection) - 1:
            row_collection.move(len(row_collection) - 1, row_insert_index)

        for view_item in view_collection:
            try:
                row_index = max(1, int(getattr(view_item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                continue
            if row_index > target_row:
                view_item.row_index = row_index + 1

        view_item = view_collection.add()
        view_uid = _izom_propui_free_layout_view_entry_uid(new_layout_uid)
        view_item.uid = view_uid
        view_item.kind = 'ENTRY_ITEM'
        view_item.layout_uid = new_layout_uid
        view_item.entry_uid = target_entry_uid
        view_item.parent_uid = ''
        view_item.row_index = target_row + 1
        view_item.column_index = 1
        view_item.row_member_uids_json = '[]'
        if target_view_index + 1 < len(view_collection) - 1:
            view_collection.move(len(view_collection) - 1, target_view_index + 1)
        for ui_order, item in enumerate(view_collection, start=1):
            item.ui_order = ui_order

        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_items')
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_rows')
        _izom_propui_free_bump_collection_revision(params, 'izom_propui_free_layout_view_items')
        _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
        izom_propui_free_invalidate_params_cache_fields(
            params,
            (
                'layout_snapshots',
                'layout_item_lookup',
                'visible_layout_rows',
                'generated_layout_state',
                'runtime_layout_entries',
            ),
        )
    finally:
        _izom_propui_free_resume_list_context_updates(params)
    return new_layout_uid

def _izom_propui_free_append_layout_entries(
    layout_snapshots,
    entry_uids,
    *,
    after_layout_uid='',
    add_into_active_row=False,
    params=None,
    target_container_uid='',
):
    target_entry_uids = [
        str(entry_uid or '').strip()
        for entry_uid in (entry_uids or ())
        if str(entry_uid or '').strip()
    ]
    if not target_entry_uids:
        return []

    target_layout_uid = str(after_layout_uid or '').strip()

    if not layout_snapshots and not add_into_active_row:
        inserted_snapshots = [
            _izom_propui_free_make_fast_ordered_layout_snapshot(offset + 1, entry_uid)
            for offset, entry_uid in enumerate(target_entry_uids)
        ]
        layout_snapshots.extend(inserted_snapshots)
        return inserted_snapshots

    if not add_into_active_row and target_layout_uid:
        inserted = _izom_propui_free_append_layout_single_rows_direct(
            layout_snapshots,
            target_entry_uids,
            after_layout_uid=target_layout_uid,
        )
        if inserted:
            return inserted

    rows = _izom_propui_free_layout_rows_from_items(layout_snapshots, params=params, visible_only=bool(params))
    snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in layout_snapshots or []
        if str(snap.get('uid', '') or '').strip()
    }
    inserted_snapshots = [
        _izom_propui_free_make_default_layout_snapshot(len(layout_snapshots) + offset + 1, entry_uid=entry_uid)
        for offset, entry_uid in enumerate(target_entry_uids)
    ]
    inserted_layout_uids = [str(snap.get('uid', '') or '').strip() for snap in inserted_snapshots]

    add_into_target_row = bool(add_into_active_row and target_layout_uid)
    if add_into_target_row:
        if not target_layout_uid and layout_snapshots:
            target_layout_uid = str(layout_snapshots[-1].get('uid', '') or '').strip()
        row_index, column_index = _izom_propui_free_layout_item_position(rows, target_layout_uid)
        if row_index < 0:
            rows.append(list(inserted_layout_uids))
        else:
            row = rows[row_index]
            insert_index = min(len(row), column_index + 1)
            row[insert_index:insert_index] = inserted_layout_uids
    else:
        row_index, _column_index = _izom_propui_free_layout_item_position(rows, target_layout_uid)
        insert_index = row_index + 1 if row_index >= 0 else len(rows)
        rows[insert_index:insert_index] = [[layout_uid] for layout_uid in inserted_layout_uids]

    layout_snapshots.extend(inserted_snapshots)
    layout_snapshots[:] = _izom_propui_free_apply_layout_rows_to_items(layout_snapshots, rows, params=params)
    return inserted_snapshots

def _izom_propui_free_append_layout_entry(
    layout_snapshots,
    entry_uid,
    *,
    after_layout_uid='',
    add_into_active_row=False,
    params=None,
    target_container_uid='',
):
    inserted = _izom_propui_free_append_layout_entries(
        layout_snapshots,
        [entry_uid],
        after_layout_uid=after_layout_uid,
        add_into_active_row=add_into_active_row,
        params=params,
        target_container_uid=target_container_uid,
    )
    return inserted[0] if inserted else None

def _izom_propui_free_import_entries_into_layout(
    layout_snapshots,
    entry_uids,
    *,
    after_layout_uid='',
    safe_import=True,
    add_into_active_row=False,
    params=None,
    target_container_uid='',
):
    target_entry_uids = [
        str(entry_uid or '').strip()
        for entry_uid in (entry_uids or ())
        if str(entry_uid or '').strip()
    ]
    if not target_entry_uids:
        return []
    if safe_import:
        existing_entry_uids = _izom_propui_free_layout_entry_uid_set(layout_snapshots)
        filtered_entry_uids = []
        for entry_uid in target_entry_uids:
            if entry_uid in existing_entry_uids:
                continue
            filtered_entry_uids.append(entry_uid)
            existing_entry_uids.add(entry_uid)
        target_entry_uids = filtered_entry_uids
    return _izom_propui_free_append_layout_entries(
        layout_snapshots,
        target_entry_uids,
        after_layout_uid=after_layout_uid,
        add_into_active_row=add_into_active_row,
        params=params,
        target_container_uid=target_container_uid,
    )

def _izom_propui_free_import_entry_into_layout(
    layout_snapshots,
    entry_uid,
    *,
    after_layout_uid='',
    safe_import=True,
    add_into_active_row=False,
    params=None,
    target_container_uid='',
):
    inserted = _izom_propui_free_import_entries_into_layout(
        layout_snapshots,
        [entry_uid],
        after_layout_uid=after_layout_uid,
        safe_import=safe_import,
        add_into_active_row=add_into_active_row,
        params=params,
        target_container_uid=target_container_uid,
    )
    return inserted[0] if inserted else None

def _izom_propui_free_next_list_focus_uid(ordered_uids, removed_uids, focus_uid):
    ordered = [str(uid or '').strip() for uid in (ordered_uids or []) if str(uid or '').strip()]
    removed = {str(uid or '').strip() for uid in (removed_uids or []) if str(uid or '').strip()}
    if not ordered:
        return ''
    focus_uid = str(focus_uid or '').strip()
    if focus_uid in ordered:
        focus_index = ordered.index(focus_uid)
    else:
        focus_index = 0
    survivors = [uid for uid in ordered if uid not in removed]
    if not survivors:
        return ''
    return survivors[min(focus_index, len(survivors) - 1)]

def _izom_propui_free_next_layout_focus_uid(ordered_uids, removed_uids, focus_uid):
    return _izom_propui_free_next_list_focus_uid(ordered_uids, removed_uids, focus_uid)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
