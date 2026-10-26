# SPDX-License-Identifier: GPL-3.0-or-later

from .cache_common import (
    _izom_propui_free_cache_public,
    _izom_propui_free_cached_params_field,
    _izom_propui_free_params_cache_entry,
)
from .entry_ids import _izom_propui_free_entry_label
from .runtime_inheritance import (
    _izom_propui_free_visibility_inheritance_scope,
)



def _izom_propui_free_snapshot_tree_entries(entry_snapshots):
    snapshots = []
    for entry in entry_snapshots or []:
        entry_uid = str(entry.get('uid', '') or '').strip()
        if not entry_uid:
            continue
        snapshots.append(
            {
                'uid': entry_uid,
                'parent_uid': str(entry.get('parent_uid', '') or '').strip(),
            }
        )
    return snapshots


def _izom_propui_free_snapshot_entry_navigation_items(params):
    entries = getattr(params, 'izom_propui_free_entries', None) or []
    snapshots = []
    for entry in entries:
        entry_uid = str(getattr(entry, 'uid', '') or '').strip()
        if not entry_uid:
            continue
        snapshots.append({
            'uid': entry_uid,
            'parent_uid': str(getattr(entry, 'parent_uid', '') or '').strip(),
            'label': str(getattr(entry, 'label', '') or '').strip(),
            'prop_id': str(getattr(entry, 'prop_id', '') or '').strip(),
            'editor_label': str(getattr(entry, 'editor_label', '') or '').strip(),
            'prop_type': str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT',
            'text_role': str(getattr(entry, 'text_role', 'TEXT') or 'TEXT').strip().upper() or 'TEXT',
            'text_alert': bool(getattr(entry, 'text_alert', False)),
        })
    return snapshots


def _izom_propui_free_inheritance_summary(applied_depth):
    depth_value = max(0, int(applied_depth or 0))
    if depth_value <= 0:
        return 'none'
    if depth_value == 1:
        return 'parent'
    if depth_value == 2:
        return "parent (+parent's rule)"
    upstream_rules = depth_value - 1
    rule_label = 'rule' if upstream_rules == 1 else 'rules'
    return f"parent (+{upstream_rules} upstream {rule_label})"


def _izom_propui_free_build_inheritance_scope_map(params, runtime_entries, tree_state, builder):
    scope_map = {}
    for entry in runtime_entries:
        entry_uid = str(entry.get('uid', '') or '').strip()
        if not entry_uid:
            continue
        scope_map[entry_uid] = builder(params, entry, state=tree_state)
    return scope_map


def _izom_propui_free_scope_info_from_scope(scope):
    resolved_scope = dict(scope or {})
    available_depth = int(resolved_scope.get('available_depth', 0) or 0)
    selected_depth = int(resolved_scope.get('selected_depth', 1) or 1)
    applied_depth = int(resolved_scope.get('applied_depth', 0) or 0)
    applied_ancestors = list(resolved_scope.get('applied_ancestors', []) or [])
    selected_ancestor = applied_ancestors[applied_depth - 1] if applied_depth > 0 and applied_depth <= len(applied_ancestors) else None
    summary_text = _izom_propui_free_inheritance_summary(applied_depth)
    return {
        'requested_depth': int(resolved_scope.get('requested_depth', selected_depth) or selected_depth),
        'available_depth': available_depth,
        'selected_depth': selected_depth,
        'applied_depth': applied_depth,
        'applied_ancestors': applied_ancestors,
        'selected_ancestor': selected_ancestor,
        'selected_relation': summary_text,
        'selected_ancestor_name': _izom_propui_free_entry_label(selected_ancestor) if selected_ancestor is not None else 'Entry',
        'summary_text': summary_text,
        'enabled': available_depth > 1,
    }


def _izom_propui_free_build_inheritance_info_map(scope_map):
    return {
        entry_uid: _izom_propui_free_scope_info_from_scope(scope)
        for entry_uid, scope in (scope_map or {}).items()
    }


def _izom_propui_free_entry_tree_for_inheritance(params, runtime_entries=None, tree_state=None):
    if runtime_entries is not None and tree_state is not None:
        return runtime_entries, tree_state
    from .cache_state import izom_propui_free_cached_entry_tree_bundle as fallback_cached_entry_tree_bundle

    cached_entry_tree_bundle = _izom_propui_free_cache_public(
        'izom_propui_free_cached_entry_tree_bundle',
        fallback_cached_entry_tree_bundle,
    )

    entry_bundle = cached_entry_tree_bundle(params)
    return (
        runtime_entries if runtime_entries is not None else entry_bundle.get('runtime_entries', []),
        tree_state if tree_state is not None else entry_bundle.get('tree_state', {}),
    )


def _izom_propui_free_update_assembled_state_inheritance(params, scope_field, scopes, info_field, info):
    cache_entry = _izom_propui_free_params_cache_entry(params)
    assembled = cache_entry.get('assembled_bundles', {}) if cache_entry is not None else {}
    bundle = assembled.get('bundle') if assembled else None
    if isinstance(bundle, dict):
        bundle[scope_field] = scopes
        bundle[info_field] = info


def izom_propui_free_cached_visibility_inheritance_info_map(params, *, runtime_entries=None, tree_state=None):
    if params is None:
        return {}
    runtime_entries, tree_state = _izom_propui_free_entry_tree_for_inheritance(
        params,
        runtime_entries=runtime_entries,
        tree_state=tree_state,
    )
    build_scope_map = _izom_propui_free_cache_public(
        '_izom_propui_free_build_inheritance_scope_map',
        _izom_propui_free_build_inheritance_scope_map,
    )
    visibility_scopes = _izom_propui_free_cached_params_field(
        params,
        'visibility_scopes',
        lambda: build_scope_map(
            params,
            runtime_entries,
            tree_state,
            _izom_propui_free_visibility_inheritance_scope,
        ),
    )
    visibility_info = _izom_propui_free_cached_params_field(
        params,
        'visibility_inheritance_info',
        lambda: _izom_propui_free_build_inheritance_info_map(visibility_scopes),
    )
    _izom_propui_free_update_assembled_state_inheritance(
        params,
        'visibility_scopes',
        visibility_scopes,
        'visibility_inheritance_info',
        visibility_info,
    )
    return visibility_info


def _izom_propui_free_build_entry_draw_state(runtime_entries, tree_state, entry_collapsed_uid_set):
    children_by_uid = tree_state.get('children_by_uid', {}) if isinstance(tree_state, dict) else {}
    depth_by_uid = tree_state.get('depth_by_uid', {}) if isinstance(tree_state, dict) else {}
    by_uid = {}
    visible_hierarchy_uids = []
    visible_entry_list_uids = []

    for entry in runtime_entries:
        entry_uid = str(entry.get('uid', '') or '').strip()
        if not entry_uid:
            continue

        parent_uid = str(entry.get('parent_uid', '') or '').strip()
        parent_state = by_uid.get(parent_uid) if parent_uid else None
        collapsed_by_ancestor = bool(parent_state.get('collapsed_branch', False)) if parent_state else False
        collapsed = entry_uid in entry_collapsed_uid_set
        visible_in_hierarchy = True
        visible_in_entry_list = not collapsed_by_ancestor

        has_children = bool(entry.get('has_children', False)) or entry_uid in children_by_uid
        # Precompute the per-row icon so the UIList draw_item can stay at one
        # property access (icon lookup) + one widget call per row, matching
        # native-speed UIList performance. Icon IDs:
        #   - parent + expanded  -> DOWNARROW_HLT
        #   - parent + collapsed -> RIGHTARROW
        #   - leaf (any depth)   -> BLANK1 (reserves the icon slot so labels
        #                           stay vertically aligned with parent rows)
        if has_children:
            row_icon = 'RIGHTARROW' if collapsed else 'DOWNARROW_HLT'
        else:
            row_icon = 'BLANK1'

        entry_state = {
            'uid': entry_uid,
            'depth': int(depth_by_uid.get(entry_uid, entry.get('depth', 0)) or 0),
            'has_children': has_children,
            'collapsed': collapsed,
            'collapsed_by_ancestor': collapsed_by_ancestor,
            'visible_in_hierarchy': visible_in_hierarchy,
            'visible_in_entry_list': visible_in_entry_list,
            'collapsed_branch': collapsed or collapsed_by_ancestor,
            'row_icon': row_icon,
        }
        by_uid[entry_uid] = entry_state

        if visible_in_hierarchy:
            visible_hierarchy_uids.append(entry_uid)
        if visible_in_entry_list:
            visible_entry_list_uids.append(entry_uid)

    return {
        'by_uid': by_uid,
        'visible_hierarchy_uids': visible_hierarchy_uids,
        'visible_hierarchy_uid_set': set(visible_hierarchy_uids),
        'visible_hierarchy_index_by_uid': {
            entry_uid: index
            for index, entry_uid in enumerate(visible_hierarchy_uids)
        },
        'visible_entry_list_uids': visible_entry_list_uids,
        'visible_entry_list_uid_set': set(visible_entry_list_uids),
        'visible_entry_list_index_by_uid': {
            entry_uid: index
            for index, entry_uid in enumerate(visible_entry_list_uids)
        },
    }


def _izom_propui_free_build_entry_index_by_uid(entry_snapshots):
    index_by_uid = {}
    for index, entry in enumerate(entry_snapshots or []):
        entry_uid = str(entry.get('uid', '') or '').strip()
        if not entry_uid:
            continue
        index_by_uid[entry_uid] = index
    return index_by_uid


def _izom_propui_free_build_same_type_peer_counts(entry_snapshots):
    type_counts = {}
    entry_types = {}
    for entry in entry_snapshots or []:
        entry_uid = str(entry.get('uid', '') or '').strip()
        if not entry_uid:
            continue
        entry_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
        entry_types[entry_uid] = entry_type
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1

    return {
        entry_uid: max(0, int(type_counts.get(entry_type, 1) or 1) - 1)
        for entry_uid, entry_type in entry_types.items()
    }


def izom_propui_free_cached_same_type_peer_counts(params, entry_snapshots=None):
    if params is None:
        return {}
    if entry_snapshots is None:
        entry_snapshots = _izom_propui_free_cached_params_field(
            params,
            'entry_navigation_snapshots',
            lambda: _izom_propui_free_snapshot_entry_navigation_items(params),
        )
    return _izom_propui_free_cached_params_field(
        params,
        'same_type_peer_counts',
        lambda: _izom_propui_free_build_same_type_peer_counts(entry_snapshots),
    )

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
