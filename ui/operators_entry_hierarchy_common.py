# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import izom_propui_free_log_recovered

from ..core.snapshots import (
    _izom_propui_free_build_state_from_snapshots,
)
from .helpers import (
    _izom_propui_free_collection_revision,
)


def _izom_propui_free_snapshot_parent_uid(snap):
    return str((snap or {}).get('parent_uid', '') or '').strip()


def _izom_propui_free_previous_sibling_uid_from_state(state, uid):
    return str(
        (state or {}).get('previous_sibling_by_uid', {}).get(str(uid or '').strip(), '') or ''
    ).strip()


def _izom_propui_free_top_ancestor_uid_from_state(snapshots, index_by_uid, uid):
    current_uid = str(uid or '').strip()
    seen = set()
    top_uid = current_uid
    while current_uid and current_uid not in seen:
        seen.add(current_uid)
        index = index_by_uid.get(current_uid)
        if index is None:
            break
        parent_uid = _izom_propui_free_snapshot_parent_uid(snapshots[index])
        if not parent_uid:
            break
        top_uid = parent_uid
        current_uid = parent_uid
    return top_uid


def _izom_propui_free_nearest_selected_ancestor_uid(snapshots, index_by_uid, uid, selected_uids):
    current_uid = str(uid or '').strip()
    if not current_uid or not selected_uids:
        return ''

    seen = set()
    parent_uid = _izom_propui_free_snapshot_parent_uid(snapshots[index_by_uid[current_uid]]) if current_uid in index_by_uid else ''
    while parent_uid and parent_uid not in seen:
        if parent_uid in selected_uids:
            return parent_uid
        seen.add(parent_uid)
        parent_index = index_by_uid.get(parent_uid)
        if parent_index is None:
            break
        parent_uid = _izom_propui_free_snapshot_parent_uid(snapshots[parent_index])
    return ''


_IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE = {}
_IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE_LIMIT = 32
_IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE = {}
_IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE_LIMIT = 16
_IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE = {}
_IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE_LIMIT = 16
_IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_clear_hierarchy_session_caches():
    _IZOM_PROPUI_FREE_SET_PARENT_ITEMS_CACHE.clear()
    _IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE.clear()
    _IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE.clear()


def _izom_propui_free_params_pointer_key(params):
    try:
        return int(params.as_pointer())
    except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return id(params)


def _izom_propui_free_hierarchy_light_tree_cache_key(params, *, include_value_fields=False):
    if params is None:
        return None
    entries = getattr(params, 'izom_propui_free_entries', None)
    try:
        entry_count = len(entries) if entries is not None else 0
    except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        entry_count = 0
    return (
        _izom_propui_free_params_pointer_key(params),
        entry_count,
        int(_izom_propui_free_collection_revision(params, 'izom_propui_free_entries') or 0),
        bool(include_value_fields),
    )


def _izom_propui_free_hierarchy_light_tree(params, *, copy_snapshots=True, include_value_fields=False):
    include_value_fields = bool(include_value_fields)
    cache_key = _izom_propui_free_hierarchy_light_tree_cache_key(params, include_value_fields=include_value_fields)
    cached = _IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE.get(cache_key) if cache_key is not None else None
    if cached is not None:
        snapshots, entry_by_uid, state = cached
        if not bool(copy_snapshots):
            return snapshots, entry_by_uid, state
        return (
            [dict(snap) for snap in snapshots],
            {uid: dict(snap) for uid, snap in dict(entry_by_uid).items()},
            state,
        )

    entries = list(getattr(params, 'izom_propui_free_entries', ()) or ()) if params is not None else []
    snapshots = []
    entry_by_uid = {}
    index_by_uid = {}
    value_kind_fields = ()
    if include_value_fields:
        value_kind_fields = (
            'prop_type',
            'value_kind',
            'array_element_type',
            'float_array_subtype',
            'array_size',
            'editor_label',
            'label',
            'text_role',
            'prop_id',
        )
    for entry in entries:
        uid = str(getattr(entry, 'uid', '') or '').strip()
        if not uid or uid in index_by_uid:
            continue
        parent_uid = str(getattr(entry, 'parent_uid', '') or '').strip()
        snap = {
            'uid': uid,
            'parent_uid': parent_uid,
        }
        if include_value_fields:
            for field_name in value_kind_fields:
                snap[field_name] = getattr(entry, field_name, '')
        index_by_uid[uid] = len(snapshots)
        snapshots.append(snap)
        entry_by_uid[uid] = snap

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
    if not snapshots:
        state = {}
    if state is None:
        state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False)
    if cache_key is not None:
        if len(_IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE) >= _IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE_LIMIT:
            _IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE.clear()
        _IZOM_PROPUI_FREE_HIERARCHY_LIGHT_TREE_CACHE[cache_key] = (
            tuple(dict(snap) for snap in snapshots),
            {uid: dict(snap) for uid, snap in entry_by_uid.items()},
            state,
        )
    return snapshots, entry_by_uid, state


def _izom_propui_free_fast_hierarchy_menu_label(item):
    if item is None:
        return '[Missing Entry]'
    if isinstance(item, dict):
        value = item.get
    else:
        value = lambda attr_name, default='': getattr(item, attr_name, default)
    editor_label = str(value('editor_label', '') or '').strip()
    if editor_label:
        return editor_label
    label = str(value('label', '') or '').strip()
    if label:
        return label
    prop_type = str(value('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    uid = str(value('uid', '') or '').strip()
    if prop_type == 'TEXT':
        text_role = str(value('text_role', 'TEXT') or 'TEXT').strip().upper()
        if text_role == 'DIVIDER':
            return '[Divider]'
        if text_role == 'SPACER':
            return '[Spacer]'
        return uid or 'Text'
    prop_id = str(value('prop_id', '') or '').strip()
    return prop_id or uid or 'Entry'


def _izom_propui_free_parent_menu_tree(params):
    cache_key = _izom_propui_free_hierarchy_light_tree_cache_key(params)
    cached = _IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE.get(cache_key) if cache_key is not None else None
    if cached is not None:
        return cached

    entries = list(getattr(params, 'izom_propui_free_entries', ()) or ()) if params is not None else []
    snapshots = []
    labels = {}
    for entry in entries:
        uid = str(getattr(entry, 'uid', '') or '').strip()
        if not uid:
            continue
        snap = {
            'uid': uid,
            'parent_uid': str(getattr(entry, 'parent_uid', '') or '').strip(),
            'prop_type': str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT',
            'editor_label': getattr(entry, 'editor_label', ''),
            'label': getattr(entry, 'label', ''),
            'text_role': getattr(entry, 'text_role', ''),
            'prop_id': getattr(entry, 'prop_id', ''),
        }
        snapshots.append(snap)
        labels[uid] = _izom_propui_free_fast_hierarchy_menu_label(snap)
    state = _izom_propui_free_build_state_from_snapshots(snapshots, copy_snapshots=False) if snapshots else {}
    result = (tuple(snapshots), state, labels)
    if cache_key is not None:
        if len(_IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE) >= _IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE_LIMIT:
            _IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE.clear()
        _IZOM_PROPUI_FREE_PARENT_MENU_TREE_CACHE[cache_key] = result
    return result


def _izom_propui_free_set_parent_items_cache_key(params):
    if params is None:
        return None
    try:
        params_key = _izom_propui_free_params_pointer_key(params)
    except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        params_key = id(params)
    entries = getattr(params, 'izom_propui_free_entries', None)
    try:
        entry_count = len(entries) if entries is not None else 0
    except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        entry_count = 0
    try:
        active_index = max(0, min(int(getattr(params, 'izom_propui_free_active_index', 0) or 0), max(0, entry_count - 1)))
    except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        active_index = 0
    active_uid = str(getattr(params, 'izom_propui_free_active_uid', '') or '').strip()
    if not active_uid and entries is not None and 0 <= active_index < entry_count:
        try:
            active_uid = str(getattr(entries[active_index], 'uid', '') or '').strip()
        except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            active_uid = ''
    active_key = active_uid or f'@{active_index}'
    return (
        params_key,
        entry_count,
        int(_izom_propui_free_collection_revision(params, 'izom_propui_free_entries') or 0),
        active_key,
    )


def _izom_propui_free_active_hierarchy_snapshot_info(params):
    if params is None:
        return {}, (), {}, -1, ''

    snapshots, _entry_by_uid, state = _izom_propui_free_hierarchy_light_tree(params, copy_snapshots=False)
    bundle = {'tree_state': state}
    if not snapshots:
        return bundle, (), {}, -1, ''

    index_by_uid = state.get('index_by_uid', {}) or {}
    active_uid = str(getattr(params, 'izom_propui_free_active_uid', '') or '').strip()
    active_index = index_by_uid.get(active_uid)
    if not isinstance(active_index, int):
        try:
            active_index = int(getattr(params, 'izom_propui_free_active_index', 0) or 0)
        except _IZOM_PROPUI_FREE_HIERARCHY_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            active_index = 0
        active_index = max(0, min(active_index, len(snapshots) - 1))
        active_uid = str((snapshots[active_index] or {}).get('uid', '') or '').strip()

    return bundle, snapshots, index_by_uid, active_index, active_uid


def _izom_propui_free_hierarchy_working_state(params, *, include_value_fields=False):
    if params is None:
        return {}, [], {}
    snapshots, _entry_by_uid, state = _izom_propui_free_hierarchy_light_tree(
        params,
        copy_snapshots=False,
        include_value_fields=include_value_fields,
    )
    return {'tree_state': state}, [dict(snap) for snap in snapshots], state

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
