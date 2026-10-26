# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_entries_shared_common import (
    _izom_propui_free_snapshot_index_by_uid,
)
from ..core.snapshot_tree import _izom_propui_free_build_state_from_snapshots
from .helper_selection_common import _izom_propui_free_uid_list_from_json



def _izom_propui_free_entry_order_state_direct(params):
    entries = getattr(params, 'izom_propui_free_entries', None) or []
    snapshots = []
    index_by_uid = {}
    ordered_uids = []
    for entry in entries:
        uid = str(getattr(entry, 'uid', '') or '').strip()
        if not uid or uid in index_by_uid:
            continue
        parent_uid = str(getattr(entry, 'parent_uid', '') or '').strip()
        index_by_uid[uid] = len(snapshots)
        ordered_uids.append(uid)
        snapshots.append({
            'uid': uid,
            'parent_uid': parent_uid,
            'prop_type': str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT',
            'prop_id': str(getattr(entry, 'prop_id', '') or '').strip(),
        })

    state = None
    if snapshots:
        children_by_uid = {}
        top_level_uids = []
        previous_sibling_by_uid = {}
        last_sibling_by_parent = {}
        depth_by_uid = {}
        stack = []
        valid_order = True
        for snap in snapshots:
            uid = snap['uid']
            parent_uid = snap['parent_uid']
            if parent_uid == uid or (parent_uid and parent_uid not in index_by_uid):
                valid_order = False
                break
            if parent_uid:
                try:
                    parent_depth = stack.index(parent_uid)
                except ValueError:
                    valid_order = False
                    break
                depth = parent_depth + 1
            else:
                depth = 0
            depth_by_uid[uid] = depth
            previous_sibling_by_uid[uid] = str(last_sibling_by_parent.get(parent_uid, '') or '').strip()
            if parent_uid:
                children_by_uid.setdefault(parent_uid, []).append(uid)
            else:
                top_level_uids.append(uid)
            last_sibling_by_parent[parent_uid] = uid
            if len(stack) <= depth:
                stack.append(uid)
            else:
                stack[depth] = uid
                del stack[depth + 1:]
        if valid_order:
            state = {
                'snapshots': snapshots,
                'index_by_uid': index_by_uid,
                'children_by_uid': children_by_uid,
                'top_level_uids': top_level_uids,
                'previous_sibling_by_uid': previous_sibling_by_uid,
                'depth_by_uid': depth_by_uid,
            }

    if state is None:
        state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
    normalized = state.get('snapshots', []) or []
    index_by_uid = state.get('index_by_uid', {}) or {}
    if normalized is snapshots:
        return normalized, index_by_uid, state, ordered_uids
    return normalized, index_by_uid, state, [str(snap.get('uid', '') or '').strip() for snap in normalized]


def _izom_propui_free_active_entry_uid_direct(params, snapshots=None, index_by_uid=None):
    snapshots = snapshots if snapshots is not None else []
    index_by_uid = index_by_uid or {}
    active_uid = str(getattr(params, 'izom_propui_free_active_uid', '') or '').strip()
    if active_uid and active_uid in index_by_uid:
        return active_uid
    try:
        active_index = int(getattr(params, 'izom_propui_free_active_index', 0) or 0)
    except (AttributeError, TypeError, ValueError):
        active_index = 0
    if 0 <= active_index < len(snapshots):
        index_uid = str(snapshots[active_index].get('uid', '') or '').strip()
        if index_uid:
            return index_uid
    return ''


def _izom_propui_free_selected_entry_uids_direct(params, snapshots, index_by_uid):
    active_uid = _izom_propui_free_active_entry_uid_direct(params, snapshots, index_by_uid)
    selected = [
        uid
        for uid in _izom_propui_free_uid_list_from_json(getattr(params, 'izom_propui_free_selected_uids_json', '[]'))
        if uid in index_by_uid
    ]
    if active_uid and selected and active_uid not in selected:
        return [active_uid]
    if selected:
        return selected
    return [active_uid] if active_uid else []


def _izom_propui_free_top_ancestor_uid(snapshots, uid):
    index_by_uid = _izom_propui_free_snapshot_index_by_uid(snapshots)
    current_uid = str(uid or '').strip()
    seen = set()
    top_uid = current_uid
    while current_uid and current_uid not in seen:
        seen.add(current_uid)
        index = index_by_uid.get(current_uid)
        if index is None:
            break
        parent_uid = str(snapshots[index].get('parent_uid', '') or '').strip()
        if not parent_uid:
            top_uid = current_uid
            break
        top_uid = parent_uid
        current_uid = parent_uid
    return top_uid

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
