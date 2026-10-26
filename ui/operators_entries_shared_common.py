# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_recovered,
)

from ..core.constants import (
    IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS,
)
from ..core.value_access import izom_propui_free_entry_value_kind
from ..core.value_labels import _izom_propui_free_is_numeric_type
from .operators_layout_support import (
    _izom_propui_free_snapshot_index_by_uid,
)
from .helpers import (
    _izom_propui_free_active_entry_uid,
    _izom_propui_free_entry_by_uid,
    _izom_propui_free_active_layout_view_item,
    _izom_propui_free_layout_item_by_uid,
    _izom_propui_free_layout_view_item_by_uid,
    _izom_propui_free_layout_view_row_member_uids,
    _izom_propui_free_value_label_target_info,
)

def _izom_propui_free_layout_entry_uid_from_view_item(params, view_item):
    if params is None or view_item is None:
        return ''
    kind = str(getattr(view_item, 'kind', '') or '').strip()
    if kind == 'ENTRY_ITEM':
        layout_uid = str(getattr(view_item, 'layout_uid', '') or '').strip()
        layout_item = _izom_propui_free_layout_item_by_uid(params, layout_uid)
        return str(getattr(layout_item, 'entry_uid', '') or '').strip() if layout_item is not None else ''
    if kind != 'ROW_HEADER':
        return ''
    member_uids = _izom_propui_free_layout_view_row_member_uids(view_item)
    if not member_uids:
        return ''
    layout_item = _izom_propui_free_layout_item_by_uid(params, member_uids[0])
    return str(getattr(layout_item, 'entry_uid', '') or '').strip() if layout_item is not None else ''


def _izom_propui_free_active_layout_row_header_item(params, *, active_view_item=None):
    resolved_active_view_item = active_view_item or _izom_propui_free_active_layout_view_item(params)
    if resolved_active_view_item is None:
        return None
    kind = str(getattr(resolved_active_view_item, 'kind', '') or '').strip()
    if kind == 'ROW_HEADER':
        return resolved_active_view_item
    if kind != 'ENTRY_ITEM':
        return None
    parent_uid = str(getattr(resolved_active_view_item, 'parent_uid', '') or '').strip()
    if not parent_uid:
        return None
    return _izom_propui_free_layout_view_item_by_uid(params, parent_uid)


def _izom_propui_free_entry_target_depth(state, parent_uid):
    target_parent_uid = str(parent_uid or '').strip()
    if not target_parent_uid:
        return 0
    return int(state['depth_by_uid'].get(target_parent_uid, 0) or 0) + 1


def _izom_propui_free_snapshot_is_numeric_entry(snapshot):
    if isinstance(snapshot, dict):
        prop_type = str((snapshot or {}).get('prop_type', '') or 'FLOAT')
    else:
        prop_type = str(getattr(snapshot, 'prop_type', '') or 'FLOAT')
    value_kind = str(
        izom_propui_free_entry_value_kind(snapshot, prop_type)
        or 'FLOAT'
    ).strip().upper() or 'FLOAT'
    return _izom_propui_free_is_numeric_type(value_kind) or value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}


def _izom_propui_free_entry_type_label(prop_type):
    normalized_type = str(prop_type or 'FLOAT').strip().upper() or 'FLOAT'
    return IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS.get(normalized_type, 'Entry')


def _izom_propui_free_editor_context_mode(editor_context):
    return 'LAYOUT' if str(editor_context or '').strip().upper() == 'LAYOUT' else 'HIERARCHY'


def _izom_propui_free_entry_operator_description(action, *, editor_context='HIERARCHY', direction='UP'):
    mode = _izom_propui_free_editor_context_mode(editor_context)
    if action == 'add':
        if mode == 'LAYOUT':
            return "Import the selected Entry List entry into Generated Layout after the active Generated Layout item"
        return "Insert a new entry after the active entry block, or at the end if nothing is active"
    if action == 'remove':
        if mode == 'LAYOUT':
            return "Remove the selected Generated Layout item or row group without deleting the Entry List entry"
        return "Remove the selected entry. Parent entries offer Delete or Delete Hierarchy"
    if action == 'duplicate':
        if mode == 'LAYOUT':
            return "Duplicate the selected Generated Layout item or row group inside Generated Layout"
        return "Duplicate the selected Entry List entry blocks after the current selection"
    if action == 'move':
        direction_label = 'up' if str(direction or 'UP').strip().upper() == 'UP' else 'down'
        if mode == 'LAYOUT':
            return f"Move the selected Generated Layout item or row group {direction_label}"
        return f"Move the selected entry together with its child subtree {direction_label}"
    return ""


def _izom_propui_free_target_entry(params, target_uid=''):
    if params is None:
        return None
    resolved_uid = str(target_uid or '').strip()
    if resolved_uid:
        entry = _izom_propui_free_entry_by_uid(params, resolved_uid)
        if entry is not None:
            return entry
    active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
    if active_uid:
        entry = _izom_propui_free_entry_by_uid(params, active_uid)
        if entry is not None:
            return entry
    entries = list(getattr(params, 'izom_propui_free_entries', []) or [])
    if not entries:
        return None
    try:
        active_index = max(0, min(int(getattr(params, 'izom_propui_free_active_index', 0) or 0), len(entries) - 1))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        active_index = 0
    return entries[active_index]


def _izom_propui_free_target_icon_owner(params, context, scope, entry_uid='', value_label_uid='', target_mode='SELF'):
    normalized_scope = str(scope or 'ENTRY').strip().upper() or 'ENTRY'
    if normalized_scope == 'PARAMS':
        return params
    if normalized_scope == 'VALUE_LABEL':
        entry = _izom_propui_free_target_entry(params, entry_uid)
        info = _izom_propui_free_value_label_target_info(entry, context, target_mode) if entry is not None else None
        collection = list(info.get('collection', []) or []) if isinstance(info, dict) else []
        target_uid = str(value_label_uid or '').strip()
        if target_uid:
            for item in collection:
                if str(getattr(item, 'uid', '') or '').strip() == target_uid:
                    return item
        if isinstance(info, dict):
            try:
                active_index = int(getattr(info.get('active_owner'), info.get('active_attr', ''), 0) or 0)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                active_index = 0
            if 0 <= active_index < len(collection):
                return collection[active_index]
            if collection:
                return collection[0]
        return None
    return _izom_propui_free_target_entry(params, entry_uid)


def _izom_propui_free_icon_property_group(prop_name):
    normalized = str(prop_name or '').strip()
    groups = {
        'text_icon': ('text_icon', 'text_icon_after'),
        'text_icon_after': ('text_icon', 'text_icon_after'),
    }
    return groups.get(normalized)


def _izom_propui_free_same_type_entry_snapshots(snapshots, target_uid):
    target_uid = str(target_uid or '').strip()
    if not target_uid:
        return []

    target_snapshot = next(
        (snap for snap in snapshots if str(snap.get('uid', '') or '').strip() == target_uid),
        None,
    )
    if target_snapshot is None:
        return []

    target_type = str(target_snapshot.get('prop_type', '') or '').strip().upper()
    return [
        snap for snap in snapshots
        if str(snap.get('uid', '') or '').strip()
        and str(snap.get('prop_type', '') or '').strip().upper() == target_type
    ]


def _izom_propui_free_active_snapshot_index(params, snapshots, *, editor_context='HIERARCHY'):
    if params is None or not snapshots:
        return -1
    active_uid = _izom_propui_free_active_entry_uid(params, editor_context=editor_context)
    if active_uid:
        index_by_uid = _izom_propui_free_snapshot_index_by_uid(snapshots)
        if active_uid in index_by_uid:
            return int(index_by_uid[active_uid])
    try:
        fallback_index = int(getattr(params, 'izom_propui_free_active_index', 0) or 0)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        fallback_index = 0
    return max(0, min(fallback_index, len(snapshots) - 1))


def _izom_propui_free_selected_root_uids(snapshots, selected_uids, *, index_by_uid=None):
    selected = {str(uid or '').strip() for uid in (selected_uids or []) if str(uid or '').strip()}
    if not selected:
        return []
    index_by_uid = dict(index_by_uid or _izom_propui_free_snapshot_index_by_uid(snapshots))
    roots = []
    for snap in snapshots:
        uid = str(snap.get('uid', '') or '').strip()
        if uid not in selected:
            continue
        parent_uid = str(snap.get('parent_uid', '') or '').strip()
        skip = False
        seen = set()
        while parent_uid and parent_uid not in seen:
            if parent_uid in selected:
                skip = True
                break
            seen.add(parent_uid)
            parent_index = index_by_uid.get(parent_uid)
            parent_uid = str(snapshots[parent_index].get('parent_uid', '') or '').strip() if parent_index is not None else ''
        if not skip:
            roots.append(uid)
    return roots


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
