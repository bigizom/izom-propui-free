# SPDX-License-Identifier: GPL-3.0-or-later

from .cache_layout import (
    _izom_propui_free_build_generated_layout_state,
    _izom_propui_free_build_layout_item_lookup,
    _izom_propui_free_build_visible_layout_rows,
    _izom_propui_free_cache_public,
    _izom_propui_free_cached_params_field,
)
from .cache_common import (
    _izom_propui_free_cached_uid_json_list,
    _izom_propui_free_params_cache_entry,
)
from .cache_entries import (
    _izom_propui_free_build_entry_draw_state,
    _izom_propui_free_build_entry_index_by_uid,
    _izom_propui_free_build_same_type_peer_counts,
    _izom_propui_free_snapshot_entry_navigation_items,
    _izom_propui_free_snapshot_tree_entries,
)
from .runtime_entries import _izom_propui_free_runtime_entries_from_snapshot_state
from .snapshot_entries_runtime import izom_propui_free_snapshot_runtime_entries
from .snapshot_layout_common import (
    izom_propui_free_snapshot_layout_items,
)
from .snapshot_tree import _izom_propui_free_build_state_from_snapshots



def izom_propui_free_cached_state_bundle(params, *, context=None):
    cache_entry = _izom_propui_free_params_cache_entry(params) if params is not None else None
    if cache_entry is not None:
        # Fast path: if the fully-assembled bundle is already cached, return
        # it without rebuilding the 20-key dict.
        # Draw passes call this dozens of times per redraw, so avoiding the
        # per-call dict allocation is a meaningful speedup during resizes.
        assembled = cache_entry.get('assembled_bundles')
        if assembled:
            cached_bundle = assembled.get('bundle')
            if cached_bundle is not None:
                return cached_bundle
    return _izom_propui_free_cached_state_bundle_inner(params, context=context)


def izom_propui_free_cached_entry_tree_bundle(params, *, context=None):
    cache_entry = _izom_propui_free_params_cache_entry(params) if params is not None else None
    if cache_entry is not None:
        assembled = cache_entry.get('assembled_bundles')
        if assembled:
            cached_bundle = assembled.get('entry_tree_bundle')
            if cached_bundle is not None:
                return cached_bundle
    return _izom_propui_free_cached_entry_tree_bundle_inner(params, context=context)


def izom_propui_free_cached_runtime_entries(params):
    if params is None:
        return []
    snapshot_runtime_entries = _izom_propui_free_cache_public(
        'izom_propui_free_snapshot_runtime_entries',
        izom_propui_free_snapshot_runtime_entries,
    )
    build_state = _izom_propui_free_cache_public(
        '_izom_propui_free_build_state_from_snapshots',
        _izom_propui_free_build_state_from_snapshots,
    )
    runtime_from_snapshot_state = _izom_propui_free_cache_public(
        '_izom_propui_free_runtime_entries_from_snapshot_state',
        _izom_propui_free_runtime_entries_from_snapshot_state,
    )
    runtime_snapshots = _izom_propui_free_cached_params_field(
        params,
        'runtime_entry_snapshots',
        lambda: snapshot_runtime_entries(params),
    )
    runtime_tree_state = _izom_propui_free_cached_params_field(
        params,
        'runtime_tree_state',
        lambda: build_state(runtime_snapshots),
    )
    return _izom_propui_free_cached_params_field(
        params,
        'runtime_entries',
        lambda: runtime_from_snapshot_state(
            runtime_snapshots,
            runtime_tree_state,
        ),
    )


def izom_propui_free_cached_runtime_parent_lookup(params):
    if params is None:
        return {}
    return _izom_propui_free_cached_params_field(
        params,
        'parent_lookup',
        lambda: {
            str(entry.get('uid', '') or '').strip(): entry
            for entry in izom_propui_free_cached_runtime_entries(params)
            if str(entry.get('uid', '') or '').strip()
        },
    )


def izom_propui_free_cached_entry_navigation_bundle(params, *, context=None):
    cache_entry = _izom_propui_free_params_cache_entry(params) if params is not None else None
    if cache_entry is not None:
        assembled = cache_entry.get('assembled_bundles')
        if assembled:
            cached_bundle = assembled.get('entry_navigation_bundle')
            if cached_bundle is not None:
                return cached_bundle
    return _izom_propui_free_cached_entry_navigation_bundle_inner(params, context=context)


def _izom_propui_free_cached_entry_navigation_bundle_inner(params, *, context=None):
    if params is None:
        return {
            'entry_snapshots': [],
            'entry_tree_snapshots': [],
            'entry_index_by_uid': {},
            'tree_state': {
                'snapshots': [],
                'index_by_uid': {},
                'children_by_uid': {},
                'depth_by_uid': {},
            },
            'entry_draw_state': {
                'by_uid': {},
                'visible_hierarchy_uids': [],
                'visible_hierarchy_uid_set': set(),
                'visible_hierarchy_index_by_uid': {},
                'visible_entry_list_uids': [],
                'visible_entry_list_uid_set': set(),
                'visible_entry_list_index_by_uid': {},
            },
            'entry_collapsed_uids': [],
            'entry_collapsed_uid_set': set(),
        }

    snapshot_navigation_items = _izom_propui_free_cache_public(
        '_izom_propui_free_snapshot_entry_navigation_items',
        _izom_propui_free_snapshot_entry_navigation_items,
    )
    build_state = _izom_propui_free_cache_public(
        '_izom_propui_free_build_state_from_snapshots',
        _izom_propui_free_build_state_from_snapshots,
    )
    entry_snapshots = _izom_propui_free_cached_params_field(
        params,
        'entry_navigation_snapshots',
        lambda: snapshot_navigation_items(params),
    )
    entry_tree_snapshots = entry_snapshots
    entry_index_by_uid = _izom_propui_free_cached_params_field(
        params,
        'entry_navigation_index_by_uid',
        lambda: _izom_propui_free_build_entry_index_by_uid(entry_snapshots),
    )
    tree_state = _izom_propui_free_cached_params_field(
        params,
        'entry_navigation_tree_state',
        lambda: build_state(entry_snapshots),
    )
    entry_collapsed_uids = _izom_propui_free_cached_params_field(
        params,
        'entry_collapsed_uids',
        lambda: _izom_propui_free_cached_uid_json_list(
            getattr(params, 'izom_propui_free_entry_collapsed_uids_json', '[]')
        ),
    )
    entry_collapsed_uid_set = _izom_propui_free_cached_params_field(
        params,
        'entry_collapsed_uid_set',
        lambda: set(entry_collapsed_uids),
    )
    entry_draw_state = _izom_propui_free_cached_params_field(
        params,
        'entry_navigation_draw_state',
        lambda: _izom_propui_free_build_entry_draw_state(entry_snapshots, tree_state, entry_collapsed_uid_set),
    )
    bundle = {
        'entry_snapshots': entry_snapshots,
        'entry_tree_snapshots': entry_tree_snapshots,
        'entry_index_by_uid': entry_index_by_uid,
        'tree_state': tree_state,
        'entry_draw_state': entry_draw_state,
        'entry_collapsed_uids': entry_collapsed_uids,
        'entry_collapsed_uid_set': entry_collapsed_uid_set,
    }

    cache_entry = _izom_propui_free_params_cache_entry(params)
    assembled = cache_entry.setdefault('assembled_bundles', {})
    assembled['entry_navigation_bundle'] = bundle
    return bundle


def _izom_propui_free_cached_entry_tree_bundle_inner(params, *, context=None):
    if params is None:
        return {
            'entry_snapshots': [],
            'entry_tree_snapshots': [],
            'entry_index_by_uid': {},
            'same_type_peer_counts': {},
            'tree_state': {
                'snapshots': [],
                'index_by_uid': {},
                'children_by_uid': {},
                'depth_by_uid': {},
            },
            'runtime_entries': [],
            'parent_lookup': {},
            'entry_draw_state': {
                'by_uid': {},
                'visible_hierarchy_uids': [],
                'visible_hierarchy_uid_set': set(),
                'visible_hierarchy_index_by_uid': {},
                'visible_entry_list_uids': [],
                'visible_entry_list_uid_set': set(),
                'visible_entry_list_index_by_uid': {},
            },
            'entry_collapsed_uids': [],
            'entry_collapsed_uid_set': set(),
        }

    snapshot_runtime_entries = _izom_propui_free_cache_public(
        'izom_propui_free_snapshot_runtime_entries',
        izom_propui_free_snapshot_runtime_entries,
    )
    build_state = _izom_propui_free_cache_public(
        '_izom_propui_free_build_state_from_snapshots',
        _izom_propui_free_build_state_from_snapshots,
    )
    runtime_from_snapshot_state = _izom_propui_free_cache_public(
        '_izom_propui_free_runtime_entries_from_snapshot_state',
        _izom_propui_free_runtime_entries_from_snapshot_state,
    )
    entry_snapshots = _izom_propui_free_cached_params_field(
        params,
        'entry_snapshots',
        lambda: snapshot_runtime_entries(params),
    )
    entry_tree_snapshots = _izom_propui_free_cached_params_field(
        params,
        'entry_tree_snapshots',
        lambda: _izom_propui_free_snapshot_tree_entries(entry_snapshots),
    )
    entry_index_by_uid = _izom_propui_free_cached_params_field(
        params,
        'entry_index_by_uid',
        lambda: _izom_propui_free_build_entry_index_by_uid(entry_snapshots),
    )
    same_type_peer_counts = _izom_propui_free_cached_params_field(
        params,
        'same_type_peer_counts',
        lambda: _izom_propui_free_build_same_type_peer_counts(entry_snapshots),
    )
    tree_state = _izom_propui_free_cached_params_field(
        params,
        'tree_state',
        lambda: build_state(entry_tree_snapshots),
    )
    runtime_entries = _izom_propui_free_cached_params_field(
        params,
        'runtime_entries',
        lambda: runtime_from_snapshot_state(entry_snapshots, tree_state),
    )
    parent_lookup = _izom_propui_free_cached_params_field(
        params,
        'parent_lookup',
        lambda: {
            str(entry.get('uid', '') or '').strip(): entry
            for entry in runtime_entries
            if str(entry.get('uid', '') or '').strip()
        },
    )
    entry_collapsed_uids = _izom_propui_free_cached_params_field(
        params,
        'entry_collapsed_uids',
        lambda: _izom_propui_free_cached_uid_json_list(
            getattr(params, 'izom_propui_free_entry_collapsed_uids_json', '[]')
        ),
    )
    entry_collapsed_uid_set = _izom_propui_free_cached_params_field(
        params,
        'entry_collapsed_uid_set',
        lambda: set(entry_collapsed_uids),
    )
    entry_draw_state = _izom_propui_free_cached_params_field(
        params,
        'entry_draw_state',
        lambda: _izom_propui_free_build_entry_draw_state(runtime_entries, tree_state, entry_collapsed_uid_set),
    )
    bundle = {
        'entry_snapshots': entry_snapshots,
        'entry_tree_snapshots': entry_tree_snapshots,
        'entry_index_by_uid': entry_index_by_uid,
        'same_type_peer_counts': same_type_peer_counts,
        'tree_state': tree_state,
        'runtime_entries': runtime_entries,
        'parent_lookup': parent_lookup,
        'entry_draw_state': entry_draw_state,
        'entry_collapsed_uids': entry_collapsed_uids,
        'entry_collapsed_uid_set': entry_collapsed_uid_set,
    }

    cache_entry = _izom_propui_free_params_cache_entry(params)
    assembled = cache_entry.setdefault('assembled_bundles', {})
    assembled['entry_tree_bundle'] = bundle
    return bundle


def izom_propui_free_cached_layout_bundle(params, *, context=None):
    cache_entry = _izom_propui_free_params_cache_entry(params) if params is not None else None
    if cache_entry is not None:
        assembled = cache_entry.get('assembled_bundles')
        if assembled:
            cached_bundle = assembled.get('layout_bundle')
            if cached_bundle is not None:
                return cached_bundle
    return _izom_propui_free_cached_layout_bundle_inner(params, context=context)


def _izom_propui_free_cached_layout_bundle_inner(params, *, context=None):
    if params is None:
        return {
            'entry_snapshots': [],
            'entry_index_by_uid': {},
            'layout_snapshots': [],
            'layout_item_lookup': {
                'by_uid': {},
                'by_entry_uid': {},
                'index_by_uid': {},
                'ordered_uids': (),
            },
            'visible_layout_rows': [],
            'generated_layout_state': {
                'rows': (),
                'groups': (),
                'group_by_row_index': {},
                'row_by_layout_uid': {},
                'shared_row_size_by_layout_uid': {},
                'row_width_percent_label_by_layout_uid': {},
                'row_height_label_by_layout_uid': {},
                'row_height_label_by_row_index': {},
                'ordered_layout_uids': (),
            },
            'layout_collapsed_row_uids': [],
            'layout_collapsed_row_uid_set': set(),
        }

    snapshot_navigation_items = _izom_propui_free_cache_public(
        '_izom_propui_free_snapshot_entry_navigation_items',
        _izom_propui_free_snapshot_entry_navigation_items,
    )
    snapshot_layout_items = _izom_propui_free_cache_public(
        'izom_propui_free_snapshot_layout_items',
        izom_propui_free_snapshot_layout_items,
    )
    build_layout_item_lookup = _izom_propui_free_cache_public(
        '_izom_propui_free_build_layout_item_lookup',
        _izom_propui_free_build_layout_item_lookup,
    )
    entry_snapshots = _izom_propui_free_cached_params_field(
        params,
        'entry_navigation_snapshots',
        lambda: snapshot_navigation_items(params),
    )
    entry_index_by_uid = _izom_propui_free_cached_params_field(
        params,
        'entry_navigation_index_by_uid',
        lambda: _izom_propui_free_build_entry_index_by_uid(entry_snapshots),
    )
    layout_snapshots = _izom_propui_free_cached_params_field(params, 'layout_snapshots', lambda: snapshot_layout_items(params))
    layout_item_lookup = _izom_propui_free_cached_params_field(
        params,
        'layout_item_lookup',
        lambda: build_layout_item_lookup(params),
    )
    visible_layout_rows = _izom_propui_free_cached_params_field(
        params,
        'visible_layout_rows',
        lambda: _izom_propui_free_build_visible_layout_rows(layout_snapshots),
    )
    generated_layout_state = _izom_propui_free_cached_params_field(
        params,
        'generated_layout_state',
        lambda: _izom_propui_free_build_generated_layout_state(
            visible_layout_rows,
            layout_snapshots,
            entry_snapshots,
        ),
    )
    layout_collapsed_row_uids = _izom_propui_free_cached_params_field(
        params,
        'layout_collapsed_row_uids',
        lambda: _izom_propui_free_cached_uid_json_list(
            getattr(params, 'izom_propui_free_layout_collapsed_row_uids_json', '[]')
        ),
    )
    layout_collapsed_row_uid_set = _izom_propui_free_cached_params_field(
        params,
        'layout_collapsed_row_uid_set',
        lambda: set(layout_collapsed_row_uids),
    )
    bundle = {
        'entry_snapshots': entry_snapshots,
        'entry_index_by_uid': entry_index_by_uid,
        'layout_snapshots': layout_snapshots,
        'layout_item_lookup': layout_item_lookup,
        'visible_layout_rows': visible_layout_rows,
        'generated_layout_state': generated_layout_state,
        'layout_collapsed_row_uids': layout_collapsed_row_uids,
        'layout_collapsed_row_uid_set': layout_collapsed_row_uid_set,
    }

    cache_entry = _izom_propui_free_params_cache_entry(params)
    assembled = cache_entry.setdefault('assembled_bundles', {})
    assembled['layout_bundle'] = bundle
    return bundle


def _izom_propui_free_cached_state_bundle_inner(params, *, context=None):
    if params is None:
        return {
            'entry_snapshots': [],
            'entry_tree_snapshots': [],
            'entry_index_by_uid': {},
            'same_type_peer_counts': {},
            'tree_state': {
                'snapshots': [],
                'index_by_uid': {},
                'children_by_uid': {},
                'depth_by_uid': {},
            },
            'layout_snapshots': [],
            'layout_item_lookup': {
                'by_uid': {},
                'by_entry_uid': {},
                'index_by_uid': {},
                'ordered_uids': (),
            },
            'generated_layout_state': {
                'rows': (),
                'groups': (),
                'group_by_row_index': {},
                'row_by_layout_uid': {},
                'shared_row_size_by_layout_uid': {},
                'row_width_percent_label_by_layout_uid': {},
                'row_height_label_by_layout_uid': {},
                'row_height_label_by_row_index': {},
                'ordered_layout_uids': (),
            },
            'layout_collapsed_row_uids': [],
            'layout_collapsed_row_uid_set': set(),
            'runtime_entries': [],
            'parent_lookup': {},
            'visibility_scopes': {},
            'visibility_inheritance_info': {},
            'entry_draw_state': {
                'by_uid': {},
                'visible_hierarchy_uids': [],
                'visible_hierarchy_uid_set': set(),
                'visible_hierarchy_index_by_uid': {},
                'visible_entry_list_uids': [],
                'visible_entry_list_uid_set': set(),
                'visible_entry_list_index_by_uid': {},
            },
            'entry_collapsed_uids': [],
            'entry_collapsed_uid_set': set(),
        }

    cached_entry_tree_bundle = _izom_propui_free_cache_public(
        'izom_propui_free_cached_entry_tree_bundle',
        izom_propui_free_cached_entry_tree_bundle,
    )
    cached_layout_bundle = _izom_propui_free_cache_public(
        'izom_propui_free_cached_layout_bundle',
        izom_propui_free_cached_layout_bundle,
    )
    entry_bundle = cached_entry_tree_bundle(params, context=context)
    layout_bundle = cached_layout_bundle(params, context=context)

    entry_snapshots = entry_bundle.get('entry_snapshots', [])
    entry_tree_snapshots = entry_bundle.get('entry_tree_snapshots', [])
    entry_index_by_uid = entry_bundle.get('entry_index_by_uid', {})
    same_type_peer_counts = entry_bundle.get('same_type_peer_counts', {})
    tree_state = entry_bundle.get('tree_state', {})
    runtime_entries = entry_bundle.get('runtime_entries', [])
    parent_lookup = entry_bundle.get('parent_lookup', {})
    entry_draw_state = entry_bundle.get('entry_draw_state', {})
    entry_collapsed_uids = entry_bundle.get('entry_collapsed_uids', [])
    entry_collapsed_uid_set = entry_bundle.get('entry_collapsed_uid_set', set())

    layout_snapshots = layout_bundle.get('layout_snapshots', [])
    layout_item_lookup = layout_bundle.get('layout_item_lookup', {})
    generated_layout_state = layout_bundle.get('generated_layout_state', {})
    layout_collapsed_row_uids = layout_bundle.get('layout_collapsed_row_uids', [])
    layout_collapsed_row_uid_set = layout_bundle.get('layout_collapsed_row_uid_set', set())

    fields = _izom_propui_free_params_cache_entry(params).get('fields', {})
    visibility_scopes = fields.get('visibility_scopes', {})
    visibility_inheritance_info = fields.get('visibility_inheritance_info', {})

    bundle = {
        'entry_snapshots': entry_snapshots,
        'entry_tree_snapshots': entry_tree_snapshots,
        'entry_index_by_uid': entry_index_by_uid,
        'same_type_peer_counts': same_type_peer_counts,
        'tree_state': tree_state,
        'layout_snapshots': layout_snapshots,
        'layout_item_lookup': layout_item_lookup,
        'generated_layout_state': generated_layout_state,
        'layout_collapsed_row_uids': layout_collapsed_row_uids,
        'layout_collapsed_row_uid_set': layout_collapsed_row_uid_set,
        'runtime_entries': runtime_entries,
        'parent_lookup': parent_lookup,
        'visibility_scopes': visibility_scopes,
        'visibility_inheritance_info': visibility_inheritance_info,
        'entry_draw_state': entry_draw_state,
        'entry_collapsed_uids': entry_collapsed_uids,
        'entry_collapsed_uid_set': entry_collapsed_uid_set,
    }

    cache_entry = _izom_propui_free_params_cache_entry(params)
    assembled = cache_entry.setdefault('assembled_bundles', {})
    assembled['bundle'] = bundle
    return bundle

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
