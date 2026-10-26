# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_layout_selection import (
    _izom_propui_free_set_last_clicked_list_context,
    _izom_propui_free_set_last_editor_context,
)
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.snapshot_layout_common import izom_propui_free_snapshot_layout_items
from .helper_layout_common import (
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE,
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE_LIMIT,
)
from .helper_layout_rows import (
    _izom_propui_free_layout_view_row_member_uids,
    _izom_propui_free_normalize_layout_view_uid,
    _izom_propui_free_ordered_layout_snapshots,
)
from .helper_selection_collections import _izom_propui_free_collection_revision
from .helper_selection_common import _izom_propui_free_json_dumps
from .helper_selection_context import (
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
)


_IZOM_PROPUI_FREE_LAYOUT_VIEW_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_layout_view_state(params):
    if params is None:
        return {
            'items': (),
            'raw_uids': (),
            'ordered_uids': (),
            'by_uid': {},
            'collection_index_by_uid': {},
        }

    collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    try:
        collection_len = len(collection) if collection is not None else 0
    except _IZOM_PROPUI_FREE_LAYOUT_VIEW_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        collection_len = 0
    cache_key = (
        _izom_propui_free_pointer_guard_key(params),
        _izom_propui_free_pointer_guard_key(collection) if collection is not None else 0,
        collection_len,
        _izom_propui_free_collection_revision(params, 'izom_propui_free_layout_view_items'),
    )
    cached = _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    try:
        items = list(collection) if collection is not None else []
    except TypeError:
        items = []

    raw_uids = []
    ordered_pairs = []
    by_uid = {}
    collection_index_by_uid = {}
    seen_uids = set()
    for index, item in enumerate(items):
        uid = str(getattr(item, 'uid', '') or '').strip()
        if not uid or uid in seen_uids:
            continue
        seen_uids.add(uid)
        raw_uids.append(uid)
        ordered_pairs.append((index, item, uid))
        by_uid[uid] = item
        collection_index_by_uid[uid] = index

    ordered_pairs.sort(
        key=lambda triple: (
            int(getattr(triple[1], 'ui_order', triple[0] + 1) or (triple[0] + 1)),
            triple[0],
        )
    )
    result = {
        'items': tuple(items),
        'raw_uids': tuple(raw_uids),
        'ordered_uids': tuple(uid for _index, _item, uid in ordered_pairs),
        'by_uid': by_uid,
        'collection_index_by_uid': collection_index_by_uid,
    }
    if len(_IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE) >= _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE_LIMIT:
        _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE[cache_key] = result
    return result


def _izom_propui_free_layout_view_item_by_uid(params, uid):
    target_uid = _izom_propui_free_normalize_layout_view_uid(uid)
    if not target_uid or params is None:
        return None
    return _izom_propui_free_layout_view_state(params).get('by_uid', {}).get(target_uid)


def _izom_propui_free_layout_view_uid_order(params):
    if params is None:
        return []
    return list(_izom_propui_free_layout_view_state(params).get('ordered_uids', ()))


def _izom_propui_free_layout_visible_snapshots(params, layout_snapshots=None, *, snapshots_are_ordered=False):
    if layout_snapshots is None:
        return list(izom_propui_free_snapshot_layout_items(params) or [])
    return list(layout_snapshots or []) if snapshots_are_ordered else _izom_propui_free_ordered_layout_snapshots(layout_snapshots)


def _izom_propui_free_active_layout_view_item(params, *, strict_uid=False):
    if params is None:
        return None

    collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    active_uid = _izom_propui_free_normalize_layout_view_uid(
        getattr(params, 'izom_propui_free_layout_view_active_uid', '')
    )
    try:
        active_index = int(getattr(params, 'izom_propui_free_layout_view_active_index', 0) or 0)
    except _IZOM_PROPUI_FREE_LAYOUT_VIEW_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        active_index = 0
    try:
        collection_len = len(collection) if collection is not None else 0
    except _IZOM_PROPUI_FREE_LAYOUT_VIEW_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        collection_len = 0
    if collection_len:
        if 0 <= active_index < collection_len:
            candidate = collection[active_index]
            candidate_uid = _izom_propui_free_normalize_layout_view_uid(getattr(candidate, 'uid', ''))
            if (not active_uid or candidate_uid == active_uid) and str(getattr(candidate, 'kind', '') or '').strip() != 'DIVIDER':
                return candidate

    view_state = _izom_propui_free_layout_view_state(params)
    by_uid = view_state.get('by_uid', {}) or {}
    if active_uid:
        item = by_uid.get(active_uid)
        if item is not None and str(getattr(item, 'kind', '') or '').strip() != 'DIVIDER':
            return item
        if strict_uid:
            return None


    from .operators_layout_view import _izom_propui_free_sync_layout_view_selection

    selected = _izom_propui_free_sync_layout_view_selection(params, persist=False)
    active_uid = selected[-1] if selected else ''
    if not active_uid:
        active_uid = _izom_propui_free_normalize_layout_view_uid(
            getattr(params, 'izom_propui_free_layout_view_active_uid', '')
        )
    item = by_uid.get(active_uid)
    if item is not None:
        return item
    raw_uids = view_state.get('raw_uids', ())
    if not raw_uids:
        return None
    try:
        index = max(0, min(int(getattr(params, 'izom_propui_free_layout_view_active_index', 0) or 0), len(raw_uids) - 1))
    except _IZOM_PROPUI_FREE_LAYOUT_VIEW_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        index = 0
    fallback_uid = raw_uids[index] if 0 <= index < len(raw_uids) else ''
    return by_uid.get(fallback_uid)


def _izom_propui_free_set_layout_view_selection(params, selected_view_uids, *, active_uid=None, anchor_uid=None, update_list_context=False):
    if params is None:
        return []
    from .operators_layout_support import _izom_propui_free_sync_layout_view_selection

    available_order = _izom_propui_free_layout_view_uid_order(params)
    available = set(available_order)
    cleaned = []
    seen = set()
    for view_uid in selected_view_uids or []:
        uid = _izom_propui_free_normalize_layout_view_uid(view_uid)
        if not uid or uid not in available or uid in seen:
            continue
        seen.add(uid)
        cleaned.append(uid)
    target_active = _izom_propui_free_normalize_layout_view_uid(active_uid)
    if target_active not in available:
        target_active = cleaned[-1] if cleaned else (available_order[0] if available_order else '')
    if not cleaned and target_active:
        cleaned = [target_active]
    target_anchor = _izom_propui_free_normalize_layout_view_uid(anchor_uid)
    if target_anchor not in available:
        target_anchor = cleaned[0] if cleaned else target_active
    view_state = _izom_propui_free_layout_view_state(params)
    target_active_index = int(view_state.get('collection_index_by_uid', {}).get(target_active, 0) or 0)
    guard_key = None
    if not update_list_context:
        guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        try:
            params.izom_propui_free_layout_view_active_index = target_active_index
            params.izom_propui_free_layout_view_active_uid = target_active
            params.izom_propui_free_layout_view_selected_uids_json = _izom_propui_free_json_dumps(cleaned)
            params.izom_propui_free_layout_view_selection_anchor_uid = target_anchor
        except _IZOM_PROPUI_FREE_LAYOUT_VIEW_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
        _izom_propui_free_sync_layout_view_selection(params, preferred_active_uid=target_active or None)
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    if update_list_context:
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        _izom_propui_free_set_last_clicked_list_context(params, 'GL_LIST')
    return cleaned


def _izom_propui_free_active_layout_view_layout_uid(params, *, after=False):
    view_item = _izom_propui_free_active_layout_view_item(params)
    if view_item is None:
        return ''
    if str(getattr(view_item, 'kind', '') or '').strip() == 'ENTRY_ITEM':
        return str(getattr(view_item, 'layout_uid', '') or '').strip()
    member_uids = _izom_propui_free_layout_view_row_member_uids(view_item)
    if not member_uids:
        return ''
    return member_uids[-1] if after else member_uids[0]

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
