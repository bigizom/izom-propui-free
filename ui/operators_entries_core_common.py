# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.snapshots import _izom_propui_free_snapshot_entry
from .operators_entries_shared import (
    _izom_propui_free_assign_duplicate_prop_ids,
    _izom_propui_free_copy_snapshot_block,
    _izom_propui_free_insert_entry_snapshot_block_direct,
    _izom_propui_free_remove_single_entry_index_direct,
    _izom_propui_free_set_entry_selection_direct,
    _izom_propui_free_uid_list_from_json,
)
from ..core.snapshot_layout_common import izom_propui_free_snapshot_layout_items
from .helper_layout_view import _izom_propui_free_set_layout_view_selection
from .operators_layout_live_members import _izom_propui_free_remove_layout_item_for_entry_direct
from .operators_layout_mutation import _izom_propui_free_remove_layout_snapshots_by_entry_uids
from .operators_layout_restore_snapshots import _izom_propui_free_restore_layout_snapshots



def _izom_propui_free_active_layout_view_layout_uid_fast(params, *, after=False):
    if params is None:
        return ''
    collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if not collection:
        return ''
    active_uid = str(getattr(params, 'izom_propui_free_layout_view_active_uid', '') or '').strip()
    try:
        active_index = int(getattr(params, 'izom_propui_free_layout_view_active_index', 0) or 0)
    except (TypeError, ValueError):
        active_index = 0
    item = None
    if 0 <= active_index < len(collection):
        candidate = collection[active_index]
        if not active_uid or str(getattr(candidate, 'uid', '') or '').strip() == active_uid:
            item = candidate
    if item is None and active_uid:
        for candidate in collection:
            if str(getattr(candidate, 'uid', '') or '').strip() == active_uid:
                item = candidate
                break
    if item is None:
        return ''
    if str(getattr(item, 'kind', '') or '').strip() == 'ENTRY_ITEM':
        return str(getattr(item, 'layout_uid', '') or '').strip()
    member_uids = _izom_propui_free_uid_list_from_json(getattr(item, 'row_member_uids_json', '[]'))
    if not member_uids:
        return ''
    return member_uids[-1] if after else member_uids[0]


def _izom_propui_free_duplicate_active_leaf_entry_direct(params):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    if not collection:
        return ''

    selected_uids = _izom_propui_free_uid_list_from_json(
        getattr(params, 'izom_propui_free_selected_uids_json', '[]')
    )
    selected_uids = [str(uid or '').strip() for uid in selected_uids if str(uid or '').strip()]

    active_uid = str(getattr(params, 'izom_propui_free_active_uid', '') or '').strip()
    try:
        active_index = int(getattr(params, 'izom_propui_free_active_index', 0) or 0)
    except (TypeError, ValueError):
        active_index = 0

    entries = list(collection)
    if not entries:
        return ''
    if not (0 <= active_index < len(entries)):
        active_index = 0

    active_entry = entries[active_index]
    index_uid = str(getattr(active_entry, 'uid', '') or '').strip()
    if active_uid and index_uid != active_uid:
        active_entry = None
        for candidate_index, candidate in enumerate(entries):
            if str(getattr(candidate, 'uid', '') or '').strip() == active_uid:
                active_entry = candidate
                active_index = candidate_index
                index_uid = active_uid
                break
        if active_entry is None:
            return ''
    else:
        active_uid = index_uid

    if not active_uid:
        return ''
    if selected_uids and selected_uids != [active_uid]:
        return ''
    if active_index + 1 < len(entries):
        next_parent_uid = str(getattr(entries[active_index + 1], 'parent_uid', '') or '').strip()
        if next_parent_uid == active_uid:
            return ''

    source_snapshot = _izom_propui_free_snapshot_entry(active_entry)
    duplicated_block = _izom_propui_free_copy_snapshot_block([source_snapshot])
    id_snapshots = [
        {
            'uid': str(getattr(entry, 'uid', '') or '').strip(),
            'parent_uid': str(getattr(entry, 'parent_uid', '') or '').strip(),
            'prop_type': str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT',
            'prop_id': str(getattr(entry, 'prop_id', '') or '').strip(),
        }
        for entry in entries
        if str(getattr(entry, 'uid', '') or '').strip()
    ]
    _izom_propui_free_assign_duplicate_prop_ids([duplicated_block], id_snapshots)
    duplicate_uid = str(duplicated_block[0].get('uid', '') or '').strip()
    insert_index = active_index + 1
    if not duplicate_uid or not _izom_propui_free_insert_entry_snapshot_block_direct(params, duplicated_block, insert_index):
        return ''
    _izom_propui_free_set_entry_selection_direct(params, duplicate_uid, insert_index)
    return duplicate_uid


def _izom_propui_free_remove_active_leaf_entry_direct(params, prior_layout_active_uid):
    collection = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
    if not collection:
        return False

    selected_uids = _izom_propui_free_uid_list_from_json(
        getattr(params, 'izom_propui_free_selected_uids_json', '[]')
    )
    selected_uids = [str(uid or '').strip() for uid in selected_uids if str(uid or '').strip()]

    active_uid = str(getattr(params, 'izom_propui_free_active_uid', '') or '').strip()
    try:
        active_index = int(getattr(params, 'izom_propui_free_active_index', 0) or 0)
    except (TypeError, ValueError):
        active_index = 0
    if not active_uid or not (0 <= active_index < len(collection)):
        return False
    if selected_uids and selected_uids != [active_uid]:
        return False
    active_entry = collection[active_index]
    if str(getattr(active_entry, 'uid', '') or '').strip() != active_uid:
        active_entry = None
        for candidate_index, candidate in enumerate(collection):
            if str(getattr(candidate, 'uid', '') or '').strip() == active_uid:
                active_entry = candidate
                active_index = candidate_index
                break
        if active_entry is None:
            return False
    if active_index + 1 < len(collection):
        next_parent_uid = str(getattr(collection[active_index + 1], 'parent_uid', '') or '').strip()
        if next_parent_uid == active_uid:
            return False

    next_uid = ''
    next_index = 0
    if active_index + 1 < len(collection):
        next_uid = str(getattr(collection[active_index + 1], 'uid', '') or '').strip()
        next_index = active_index
    elif active_index > 0:
        next_uid = str(getattr(collection[active_index - 1], 'uid', '') or '').strip()
        next_index = active_index - 1

    if not _izom_propui_free_remove_single_entry_index_direct(params, active_uid, active_index):
        return False

    removed_uids = {active_uid}
    layout_changed = _izom_propui_free_remove_layout_item_for_entry_direct(params, removed_uids)
    if layout_changed:
        active_layout_uid = str(prior_layout_active_uid or '').strip()
        if active_layout_uid:
            layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
            if not any(
                str(getattr(item, 'uid', '') or '').strip() == active_layout_uid
                for item in (layout_collection or ())
            ):
                active_layout_uid = ''
        if not active_layout_uid:
            _izom_propui_free_set_layout_view_selection(
                params,
                [],
                active_uid='',
                anchor_uid='',
                update_list_context=False,
            )
    else:
        layout_snapshots = [dict(snap) for snap in izom_propui_free_snapshot_layout_items(params)]
        layout_changed = _izom_propui_free_remove_layout_snapshots_by_entry_uids(layout_snapshots, removed_uids, params=params)
        if layout_changed:
            active_layout_uid = str(prior_layout_active_uid or '').strip()
            if active_layout_uid and not any(
                str(snap.get('uid', '') or '').strip() == active_layout_uid
                for snap in layout_snapshots
            ):
                active_layout_uid = ''
            _izom_propui_free_restore_layout_snapshots(
                params,
                layout_snapshots,
                active_layout_uid=active_layout_uid,
                sync_view_selection=False,
            )

    _izom_propui_free_set_entry_selection_direct(params, next_uid, next_index)
    return True


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
