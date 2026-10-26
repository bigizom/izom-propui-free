# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from ..core.cache_layout import (
    _izom_propui_free_layout_snapshot_row_count,
    izom_propui_free_cached_layout_item_lookup,
)
from ..core.cache_state import izom_propui_free_cached_layout_bundle
from ..core.context import izom_propui_free_context_params
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.snapshot_layout_common import (
    _izom_propui_free_layout_column_label,
    izom_propui_free_snapshot_layout_items,
)
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_DISPLAY_ORDER_UPDATE_GUARD
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_layout_cache
from .helper_selection_collections import _izom_propui_free_bump_collection_revision
from .helper_selection_common import (
    _izom_propui_free_ensure_collection_item_uid,
    _izom_propui_free_entry_by_uid,
    _izom_propui_free_set_attr_if_changed,
)



_IZOM_PROPUI_FREE_LAYOUT_LOOKUP_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_find_params_for_layout_item(layout_item, context=None):
    layout_uid = str(getattr(layout_item, 'uid', '') or '').strip()
    entry_uid = str(getattr(layout_item, 'entry_uid', '') or '').strip()
    for candidate_context in (context, bpy.context):
        params = izom_propui_free_context_params(candidate_context)
        if params is None:
            continue
        layout_lookup = izom_propui_free_cached_layout_bundle(params).get('layout_item_lookup', {}) or {}
        if layout_uid and layout_lookup.get('by_uid', {}).get(layout_uid) is not None:
            return params
        if entry_uid and layout_lookup.get('by_entry_uid', {}).get(entry_uid) is not None:
            return params
    return None


def _izom_propui_free_find_params_for_layout_row(layout_row, context=None):
    try:
        row_index = max(1, int(getattr(layout_row, 'row_index', 1) or 1))
    except (TypeError, ValueError):
        row_index = 1
    for candidate_context in (context, bpy.context):
        params = izom_propui_free_context_params(candidate_context)
        if params is None:
            continue
        for item in getattr(params, 'izom_propui_free_layout_rows', None) or []:
            try:
                item_row_index = max(1, int(getattr(item, 'row_index', 1) or 1))
            except (TypeError, ValueError):
                item_row_index = 1
            if item is layout_row or item_row_index == row_index:
                return params
    return None


def _izom_propui_free_layout_item_uid_order(params, *, visible_only=False):
    if params is None:
        return []
    if visible_only:
        state_bundle = izom_propui_free_cached_layout_bundle(params)
        return list(state_bundle.get('generated_layout_state', {}).get('ordered_layout_uids', ()))
    return list(izom_propui_free_cached_layout_item_lookup(params).get('ordered_uids', ()))


def _izom_propui_free_layout_item_by_uid(params, uid):
    target_uid = str(uid or '').strip()
    if not target_uid or params is None:
        return None
    return izom_propui_free_cached_layout_item_lookup(params).get('by_uid', {}).get(target_uid)


def _izom_propui_free_layout_item_by_entry_uid(params, entry_uid):
    target_uid = str(entry_uid or '').strip()
    if not target_uid or params is None:
        return None
    return izom_propui_free_cached_layout_item_lookup(params).get('by_entry_uid', {}).get(target_uid)


def _izom_propui_free_layout_row_by_index(params, row_index):
    if params is None:
        return None
    try:
        target_index = max(1, int(row_index or 1))
    except (TypeError, ValueError):
        target_index = 1
    for item in getattr(params, 'izom_propui_free_layout_rows', None) or []:
        try:
            item_row_index = max(1, int(getattr(item, 'row_index', 1) or 1))
        except (TypeError, ValueError):
            item_row_index = 1
        if item_row_index == target_index:
            return item
    return None


def _izom_propui_free_layout_visible_entry_uids(params):
    if params is None:
        return []
    state_bundle = izom_propui_free_cached_layout_bundle(params)
    layout_lookup = state_bundle.get('layout_item_lookup', {}).get('by_uid', {})
    ordered_layout_uids = state_bundle.get('generated_layout_state', {}).get('ordered_layout_uids', ())
    result = []
    for layout_uid in ordered_layout_uids:
        item = layout_lookup.get(str(layout_uid or '').strip())
        entry_uid = str(getattr(item, 'entry_uid', '') or '').strip() if item is not None else ''
        if entry_uid:
            result.append(entry_uid)
    return result


def _izom_propui_free_shared_row_group_size(params, entry=None, layout_item=None):
    if params is None:
        return 1
    if layout_item is None:
        entry_uid = str(getattr(entry, 'uid', '') or '')
        if not entry_uid:
            return 1
        layout_item = _izom_propui_free_layout_item_by_entry_uid(params, entry_uid)
    if layout_item is None:
        return 1
    layout_uid = str(getattr(layout_item, 'uid', '') or '').strip()
    return max(
        1,
        int(
            izom_propui_free_cached_layout_bundle(params)
            .get('generated_layout_state', {})
            .get('shared_row_size_by_layout_uid', {})
            .get(layout_uid, 1)
            or 1
        ),
    )


def _izom_propui_free_layout_item_column_label(params, layout_item):
    if params is None or layout_item is None:
        return ''
    row_size = _izom_propui_free_shared_row_group_size(params, layout_item=layout_item)
    return _izom_propui_free_layout_column_label(
        int(getattr(layout_item, 'column_index', 1) or 1),
        row_size,
    )


def _izom_propui_free_layout_row_count(params):
    if params is None:
        return 0
    return _izom_propui_free_layout_snapshot_row_count(izom_propui_free_snapshot_layout_items(params))

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
