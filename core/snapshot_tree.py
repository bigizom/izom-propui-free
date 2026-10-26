# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict

from .constants import IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH
from .entry_ids import _izom_propui_free_new_uid
from .float_arrays import (
    izom_propui_free_normalize_array_element_type,
    izom_propui_free_normalize_array_storage,
)
from .value_access import (
    izom_propui_free_clamp_component_slot,
    izom_propui_free_entry_component_meta,
    izom_propui_free_entry_value_kind,
)


_IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS = (TypeError, ValueError)


def _izom_propui_free_snapshot_uid(snap):
    uid = str(snap['uid'] or '').strip()
    if not uid:
        raise ValueError("Entry snapshots must contain a non-empty uid")
    return uid


def _izom_propui_free_snapshot_parent_uid(snap):
    return str(snap['parent_uid'] or '').strip()


def _izom_propui_free_coerce_int(value, default):
    try:
        return int(value)
    except _IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS:
        return int(default)


def _izom_propui_free_coerce_float(value, default):
    try:
        return float(value)
    except _IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS:
        return float(default)


def _izom_propui_free_build_state_from_snapshots(snapshots, *, copy_snapshots=True):
    snaps = [dict(snap) for snap in snapshots] if bool(copy_snapshots) else list(snapshots or ())
    raw_index_by_uid = {}
    seen_uids = set()

    for index, snap in enumerate(snaps):
        uid = _izom_propui_free_snapshot_uid(snap)
        while uid in seen_uids:
            uid = _izom_propui_free_new_uid()
        seen_uids.add(uid)
        parent_uid = _izom_propui_free_snapshot_parent_uid(snap)
        snap['uid'] = uid
        snap['parent_uid'] = parent_uid
        raw_index_by_uid[uid] = index

    parent_by_uid = {}
    for snap in snaps:
        uid = snap['uid']
        parent_uid = snap['parent_uid']
        if parent_uid == uid or parent_uid not in raw_index_by_uid:
            parent_uid = ''
        parent_by_uid[uid] = parent_uid

    for snap in snaps:
        uid = snap['uid']
        parent_uid = parent_by_uid.get(uid, '')
        seen = {uid}
        while parent_uid:
            if parent_uid in seen:
                parent_by_uid[uid] = ''
                break
            seen.add(parent_uid)
            parent_uid = parent_by_uid.get(parent_uid, '')
        snap['parent_uid'] = parent_by_uid.get(uid, '')

    children_by_uid = defaultdict(list)
    top_level_uids = []
    for snap in snaps:
        uid = snap['uid']
        parent_uid = snap['parent_uid']
        if parent_uid:
            children_by_uid[parent_uid].append(uid)
        else:
            top_level_uids.append(uid)

    ordered_uids = []
    emitted_uids = set()

    def emit(uid):
        if uid in emitted_uids:
            return
        emitted_uids.add(uid)
        ordered_uids.append(uid)
        for child_uid in children_by_uid.get(uid, ()):
            emit(child_uid)

    for uid in top_level_uids:
        emit(uid)
    for snap in snaps:
        uid = snap['uid']
        if uid in emitted_uids:
            continue
        snap['parent_uid'] = ''
        emit(uid)

    snap_by_uid = {snap['uid']: snap for snap in snaps}
    snaps = [snap_by_uid[uid] for uid in ordered_uids if uid in snap_by_uid]
    index_by_uid = {snap['uid']: index for index, snap in enumerate(snaps)}

    ordered_children_by_uid = defaultdict(list)
    ordered_top_level_uids = []
    previous_sibling_by_uid = {}
    last_sibling_by_parent = {}
    for snap in snaps:
        uid = snap['uid']
        parent_uid = snap['parent_uid']
        previous_sibling_by_uid[uid] = str(last_sibling_by_parent.get(parent_uid, '') or '').strip()
        if parent_uid:
            ordered_children_by_uid[parent_uid].append(uid)
        else:
            ordered_top_level_uids.append(uid)
        last_sibling_by_parent[parent_uid] = uid

    depth_by_uid = {}

    def compute_depth(uid):
        if uid in depth_by_uid:
            return depth_by_uid[uid]

        snap = snaps[index_by_uid[uid]]
        parent_uid = snap['parent_uid']
        if not parent_uid or parent_uid not in index_by_uid:
            depth = 0
        else:
            depth = compute_depth(parent_uid) + 1
        depth_by_uid[uid] = depth
        return depth

    for uid in index_by_uid:
        compute_depth(uid)

    return {
        'snapshots': snaps,
        'index_by_uid': index_by_uid,
        'children_by_uid': dict(ordered_children_by_uid),
        'top_level_uids': ordered_top_level_uids,
        'previous_sibling_by_uid': previous_sibling_by_uid,
        'depth_by_uid': depth_by_uid,
    }


def _izom_propui_free_entry_ancestor_chain_from_state(state, entry_uid):
    target_uid = str(entry_uid or '').strip()
    if not target_uid or state is None:
        return []

    index_by_uid = state.get('index_by_uid', {})
    state_snapshots = state.get('snapshots', [])
    if target_uid not in index_by_uid:
        return []

    chain = []
    current_uid = target_uid
    seen = set()
    while current_uid and current_uid not in seen:
        seen.add(current_uid)
        snap = state_snapshots[index_by_uid[current_uid]]
        parent_uid = str(snap['parent_uid'] or '').strip()
        if not parent_uid or parent_uid not in index_by_uid:
            break
        parent_snap = state_snapshots[index_by_uid[parent_uid]]
        chain.append(parent_snap)
        current_uid = parent_uid
    return chain


def _izom_propui_free_clamp_visibility_inheritance_depth(depth_value, available_depth):
    depth = _izom_propui_free_coerce_int(depth_value, 1)
    max_depth = max(1, min(int(available_depth or 1), int(IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH)))
    return max(1, min(max_depth, depth))


def _izom_propui_free_clamp_snapshot_default_value(snap):
    prop_type = str(snap['prop_type'] or 'FLOAT').strip().upper()
    if prop_type == 'FLOAT':
        min_value = _izom_propui_free_coerce_float(snap['min_float'], 0.0)
        max_value = _izom_propui_free_coerce_float(snap['max_float'], min_value)
        low = min(min_value, max_value)
        high = max(min_value, max_value)
        default_value = _izom_propui_free_coerce_float(snap['default_float'], low)
        snap['default_float'] = min(max(default_value, low), high)
    elif prop_type == 'INT':
        min_value = _izom_propui_free_coerce_int(snap['min_int'], 0)
        max_value = _izom_propui_free_coerce_int(snap['max_int'], min_value)
        low = min(min_value, max_value)
        high = max(min_value, max_value)
        default_value = _izom_propui_free_coerce_int(snap['default_int'], low)
        snap['default_int'] = min(max(default_value, low), high)
    elif prop_type == 'ARRAY':
        element_type = izom_propui_free_normalize_array_element_type(snap.get('array_element_type', 'FLOAT'), 'FLOAT')
        if element_type == 'FLOAT':
            min_value = _izom_propui_free_coerce_float(snap['min_float'], 0.0)
            max_value = _izom_propui_free_coerce_float(snap['max_float'], 1.0)
            low = min(min_value, max_value)
            high = max(min_value, max_value)
            float_array_value = izom_propui_free_normalize_array_storage(
                snap.get('default_float_array', (1.0,) * 32),
                'FLOAT',
            )
            snap['default_float_array'] = tuple(min(max(float(component), low), high) for component in float_array_value)
        elif element_type == 'INT':
            min_value = _izom_propui_free_coerce_int(snap['min_int'], 0)
            max_value = _izom_propui_free_coerce_int(snap['max_int'], min_value)
            low = min(min_value, max_value)
            high = max(min_value, max_value)
            int_array_value = izom_propui_free_normalize_array_storage(
                snap.get('default_int_array', (0,) * 32),
                'INT',
            )
            snap['default_int_array'] = tuple(min(max(int(component), low), high) for component in int_array_value)
        else:
            snap['default_bool_array'] = izom_propui_free_normalize_array_storage(
                snap.get('default_bool_array', (False,) * 32),
                'BOOL',
            )


def _izom_propui_free_snapshot_numeric_bounds(snap, prop_type):
    if prop_type == 'FLOAT':
        min_value = _izom_propui_free_coerce_float(snap['min_float'], 0.0)
        max_value = _izom_propui_free_coerce_float(snap['max_float'], min_value)
        return min(min_value, max_value), max(min_value, max_value)
    if prop_type == 'INT':
        min_value = _izom_propui_free_coerce_int(snap['min_int'], 0)
        max_value = _izom_propui_free_coerce_int(snap['max_int'], min_value)
        return min(min_value, max_value), max(min_value, max_value)
    return None, None


def _izom_propui_free_snapshot_child_compare_prop_type(parent, child, *, use_component_attr, component_attr):
    parent_value_kind = str(
        izom_propui_free_entry_value_kind(parent, str(parent.get('prop_type', '') or '').strip().upper())
        or 'NONE'
    ).strip().upper() or 'NONE'
    component_meta = izom_propui_free_entry_component_meta(parent, parent_value_kind)
    if not bool(component_meta.get('supported', False)):
        if bool(child.get(use_component_attr, False)):
            child[use_component_attr] = False
        if _izom_propui_free_coerce_int(child.get(component_attr, 1), 1) != 1:
            child[component_attr] = 1
        return parent_value_kind

    component_slot = izom_propui_free_clamp_component_slot(
        child.get(component_attr, 1),
        component_meta.get('size', 1),
        default=1,
    )
    if _izom_propui_free_coerce_int(child.get(component_attr, component_slot), component_slot) != component_slot:
        child[component_attr] = component_slot

    if not bool(child.get(use_component_attr, False)):
        return parent_value_kind

    return str(component_meta.get('component_kind', parent_value_kind) or parent_value_kind).strip().upper() or parent_value_kind


def _izom_propui_free_clamp_snapshot_compare_value(state, snap, *, prefix):
    # prefix is 'visibility' for Free's parent-relative compare fields.
    parent_uid = str(snap['parent_uid'] or '').strip()
    if not parent_uid:
        return

    index_by_uid = state.get('index_by_uid', {}) if isinstance(state, dict) else {}
    snapshots = state.get('snapshots', []) if isinstance(state, dict) else []
    parent_index = index_by_uid.get(parent_uid)
    if parent_index is None or not (0 <= int(parent_index) < len(snapshots)):
        return

    parent = snapshots[int(parent_index)]
    parent_prop_type = _izom_propui_free_snapshot_child_compare_prop_type(
        parent,
        snap,
        use_component_attr=f'{prefix}_use_component',
        component_attr=f'{prefix}_component_index',
    )
    low, high = _izom_propui_free_snapshot_numeric_bounds(parent, parent_prop_type)
    if parent_prop_type == 'FLOAT':
        compare_value = _izom_propui_free_coerce_float(snap[f'{prefix}_match_float'], low)
        snap[f'{prefix}_match_float'] = min(max(compare_value, low), high)
        range_max = _izom_propui_free_coerce_float(snap[f'{prefix}_range_max_float'], high)
        snap[f'{prefix}_range_max_float'] = min(max(range_max, low), high)
    elif parent_prop_type == 'INT':
        compare_value = _izom_propui_free_coerce_int(snap[f'{prefix}_match_int'], low)
        snap[f'{prefix}_match_int'] = min(max(compare_value, low), high)
        range_max = _izom_propui_free_coerce_int(snap[f'{prefix}_range_max_int'], high)
        snap[f'{prefix}_range_max_int'] = min(max(range_max, low), high)


def _izom_propui_free_visibility_inheritance_depth_from_state(state, entry_uid, depth_value):
    chain = _izom_propui_free_entry_ancestor_chain_from_state(state, entry_uid)
    return _izom_propui_free_clamp_visibility_inheritance_depth(depth_value, len(chain))


def _izom_propui_free_normalize_snapshot_display_rows(snapshots):
    if not snapshots:
        return

    state = _izom_propui_free_build_state_from_snapshots(snapshots)
    snapshot_by_uid = {str(snap['uid'] or ''): snap for snap in snapshots}
    ordered = []
    for state_snap in state['snapshots']:
        uid = str(state_snap['uid'] or '')
        real_snap = snapshot_by_uid.get(uid)
        if real_snap is not None:
            ordered.append(real_snap)

    used_slots_by_order = {}
    for snap in ordered:
        requested_order = max(1, _izom_propui_free_coerce_int(snap['display_order'], snap['ui_order']))
        requested_slot = max(1, _izom_propui_free_coerce_int(snap['row_slot'], 1))
        display_order = requested_order
        used_slots = used_slots_by_order.setdefault(display_order, set())
        row_slot = requested_slot
        while row_slot in used_slots:
            row_slot += 1
        used_slots.add(row_slot)
        snap['display_order'] = display_order
        snap['row_slot'] = row_slot


def _izom_propui_free_subtree_end(snapshots, start_index, *, state=None):
    state = state if state is not None else _izom_propui_free_build_state_from_snapshots(snapshots)
    state_snapshots = state['snapshots']
    index_by_uid = state['index_by_uid']
    ancestor_uid = state_snapshots[start_index]['uid']
    end = start_index + 1
    depth_by_uid = state.get('depth_by_uid') if isinstance(state, dict) else None
    if depth_by_uid:
        ancestor_depth = int(depth_by_uid.get(ancestor_uid, 0) or 0)
        while end < len(state_snapshots):
            uid = state_snapshots[end]['uid']
            if int(depth_by_uid.get(uid, 0) or 0) <= ancestor_depth:
                break
            end += 1
        return end

    while end < len(state_snapshots):
        parent_uid = state_snapshots[end]['parent_uid']
        is_descendant = False
        seen = set()
        while parent_uid and parent_uid not in seen:
            if parent_uid == ancestor_uid:
                is_descendant = True
                break
            seen.add(parent_uid)
            parent_uid = state_snapshots[index_by_uid[parent_uid]]['parent_uid']

        if not is_descendant:
            break
        end += 1

    return end


def _izom_propui_free_descendant_uids(snapshots, ancestor_uid, *, state=None):
    if not ancestor_uid:
        return set()
    state = state if state is not None else _izom_propui_free_build_state_from_snapshots(snapshots)
    state_snapshots = state['snapshots']
    index_by_uid = state['index_by_uid']
    descendants = set()
    if ancestor_uid not in index_by_uid:
        return descendants
    depth_by_uid = state.get('depth_by_uid') if isinstance(state, dict) else None
    if depth_by_uid:
        ancestor_depth = int(depth_by_uid.get(ancestor_uid, 0) or 0)
        for snap in state_snapshots[index_by_uid[ancestor_uid] + 1:]:
            uid = snap['uid']
            if int(depth_by_uid.get(uid, 0) or 0) <= ancestor_depth:
                break
            descendants.add(uid)
        return descendants
    for snap in state_snapshots:
        uid = snap['uid']
        parent_uid = snap['parent_uid']
        seen = set()
        while parent_uid and parent_uid not in seen:
            if parent_uid == ancestor_uid:
                descendants.add(uid)
                break
            seen.add(parent_uid)
            if parent_uid not in index_by_uid:
                break
            parent_uid = state_snapshots[index_by_uid[parent_uid]]['parent_uid']
    return descendants


def _izom_propui_free_move_block_up(snapshots, index, *, state=None):
    state = state if state is not None else _izom_propui_free_build_state_from_snapshots(snapshots)
    selected = state['snapshots'][index]
    parent_uid = selected['parent_uid']

    previous_sibling_index = None
    for cursor in range(index - 1, -1, -1):
        if state['snapshots'][cursor]['parent_uid'] == parent_uid:
            previous_sibling_index = cursor
            break

    if previous_sibling_index is None:
        return False

    block_end = _izom_propui_free_subtree_end(snapshots, index, state=state)
    block = snapshots[index:block_end]
    del snapshots[index:block_end]
    snapshots[previous_sibling_index:previous_sibling_index] = block
    return True


def _izom_propui_free_move_block_down(snapshots, index, *, state=None):
    state = state if state is not None else _izom_propui_free_build_state_from_snapshots(snapshots)
    selected = state['snapshots'][index]
    parent_uid = selected['parent_uid']

    block_end = _izom_propui_free_subtree_end(snapshots, index, state=state)
    next_sibling_index = None
    cursor = block_end
    while cursor < len(state['snapshots']):
        if state['snapshots'][cursor]['parent_uid'] == parent_uid:
            next_sibling_index = cursor
            break
        cursor += 1

    if next_sibling_index is None:
        return False

    next_sibling_end = _izom_propui_free_subtree_end(snapshots, next_sibling_index, state=state)
    block = snapshots[index:block_end]
    del snapshots[index:block_end]

    insert_index = next_sibling_end - len(block)
    snapshots[insert_index:insert_index] = block
    return True
