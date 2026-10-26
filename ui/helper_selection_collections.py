# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .helper_selection_context import (
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
    izom_propui_free_log_recovered,
)
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD
from .helper_cache_updates_entry_params import _izom_propui_free_find_params_for_entry
from .helper_selection_common import (
    _IZOM_PROPUI_FREE_COLLECTION_REVISION,
    _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE,
    _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE_LIMIT,
    _izom_propui_free_collection_selection_fields,
    _izom_propui_free_ensure_collection_item_uid,
    _izom_propui_free_store_uid_list,
    _izom_propui_free_uid_list_from_json,
)



def _izom_propui_free_collection_active_index_guard_key(owner, collection_name):
    return ('collection_active_index', str(collection_name or ''), _izom_propui_free_pointer_guard_key(owner))


def _izom_propui_free_set_collection_active_index_guarded(owner, collection_name, active_attr_name, value, *, category='UI'):
    try:
        if getattr(owner, active_attr_name) == value:
            return
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category=category,
            exception=exc,
        )

    guard_key = _izom_propui_free_collection_active_index_guard_key(owner, collection_name)
    _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.add(guard_key)
    try:
        try:
            setattr(owner, active_attr_name, value)
        except (AttributeError, TypeError, ValueError) as exc:
            izom_propui_free_log_recovered(
                category=category,
                exception=exc,
            )
    finally:
        _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_collection_revision_key(owner, collection_name):
    return (_izom_propui_free_pointer_guard_key(owner), str(collection_name or ''))


def _izom_propui_free_collection_revision(owner, collection_name):
    return int(_IZOM_PROPUI_FREE_COLLECTION_REVISION.get(_izom_propui_free_collection_revision_key(owner, collection_name), 0) or 0)


def _izom_propui_free_bump_collection_revision(owner, collection_name):
    key = _izom_propui_free_collection_revision_key(owner, collection_name)
    _IZOM_PROPUI_FREE_COLLECTION_REVISION[key] = int(_IZOM_PROPUI_FREE_COLLECTION_REVISION.get(key, 0) or 0) + 1
    return _IZOM_PROPUI_FREE_COLLECTION_REVISION[key]


def _izom_propui_free_set_collection_selection_direct(owner, collection_name, selected_uids, *, active_uid='', active_index=0, anchor_uid=''):
    active_attr, active_uid_attr, selected_attr, anchor_attr = _izom_propui_free_collection_selection_fields(collection_name)
    cleaned = []
    seen = set()
    for uid in selected_uids or []:
        item_uid = str(uid or '').strip()
        if item_uid and item_uid not in seen:
            cleaned.append(item_uid)
            seen.add(item_uid)
    target_active = str(active_uid or (cleaned[-1] if cleaned else '') or '').strip()
    target_anchor = str(anchor_uid or target_active or '').strip()
    try:
        target_index = max(0, int(active_index or 0))
    except (TypeError, ValueError):
        target_index = 0

    _izom_propui_free_store_uid_list(owner, selected_attr, cleaned)
    _izom_propui_free_set_collection_active_index_guarded(
        owner,
        collection_name,
        active_attr,
        target_index,
    )
    try:
        setattr(owner, active_uid_attr, target_active)
        setattr(owner, anchor_attr, target_anchor)
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    return cleaned


def _izom_propui_free_collection_state(owner, collection_name):
    if owner is None:
        return {
            'items': (),
            'order': (),
            'by_uid': {},
            'index_by_uid': {},
        }

    collection = getattr(owner, collection_name, None)
    try:
        collection_len = len(collection) if collection is not None else 0
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        collection_len = 0

    cache_key = (
        _izom_propui_free_pointer_guard_key(owner),
        str(collection_name or ''),
        _izom_propui_free_pointer_guard_key(collection) if collection is not None else 0,
        collection_len,
        _izom_propui_free_collection_revision(owner, collection_name),
    )
    cached = _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    try:
        items = list(collection) if collection is not None else []
    except TypeError:
        items = []

    order = []
    by_uid = {}
    index_by_uid = {}
    for index, item in enumerate(items):
        uid = _izom_propui_free_ensure_collection_item_uid(item)
        if not uid or uid in by_uid:
            continue
        order.append(uid)
        by_uid[uid] = item
        index_by_uid[uid] = index

    result = {
        'items': tuple(items),
        'order': tuple(order),
        'by_uid': by_uid,
        'index_by_uid': index_by_uid,
    }
    if len(_IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE) >= _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE_LIMIT:
        _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE.clear()
    _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE[cache_key] = result
    return result


def _izom_propui_free_collection_uid_order(owner, collection_name):
    return list(_izom_propui_free_collection_state(owner, collection_name).get('order', ()))


def _izom_propui_free_sync_collection_selection(owner, collection_name, *, preferred_active_uid=None, preferred_active_index=None):
    active_attr, active_uid_attr, selected_attr, anchor_attr = _izom_propui_free_collection_selection_fields(collection_name)
    selection_guard_key = _izom_propui_free_collection_active_index_guard_key(owner, collection_name)
    if selection_guard_key in _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD:
        selected = _izom_propui_free_uid_list_from_json(getattr(owner, selected_attr, '[]'))
        if selected:
            return selected
        active_uid = str(getattr(owner, active_uid_attr, '') or '').strip()
        return [active_uid] if active_uid else []

    _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.add(selection_guard_key)
    try:
        state = _izom_propui_free_collection_state(owner, collection_name)
        collection = state.get('items', ())
        order = list(state.get('order', ()))
        if not order:
            try:
                setattr(owner, active_attr, 0)
                setattr(owner, active_uid_attr, '')
                setattr(owner, anchor_attr, '')
                setattr(owner, selected_attr, '[]')
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
            return []

        available = set(order)
        active_uid = str(preferred_active_uid or '').strip()
        if not active_uid and preferred_active_index is not None:
            try:
                current_index = max(0, min(int(preferred_active_index), len(collection) - 1))
            except (TypeError, ValueError):
                current_index = 0
            active_uid = _izom_propui_free_ensure_collection_item_uid(collection[current_index])

        if not active_uid:
            stored_uid = str(getattr(owner, active_uid_attr, '') or '').strip()
            if stored_uid in available:
                active_uid = stored_uid

        if not active_uid or active_uid not in available:
            try:
                current_index = max(0, min(int(getattr(owner, active_attr, 0)), len(collection) - 1))
            except (AttributeError, TypeError, ValueError):
                current_index = 0
            active_uid = _izom_propui_free_ensure_collection_item_uid(collection[current_index])
            if active_uid and active_uid not in available:
                order.append(active_uid)
                available.add(active_uid)
        if not active_uid or active_uid not in available:
            if order:
                active_uid = order[0]
            else:
                try:
                    setattr(owner, active_attr, 0)
                    setattr(owner, active_uid_attr, '')
                    setattr(owner, anchor_attr, '')
                    setattr(owner, selected_attr, '[]')
                except (AttributeError, TypeError, ValueError) as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
                return []
        selected = [active_uid] if active_uid else []
        anchor_uid = active_uid

        active_index = int(state.get('index_by_uid', {}).get(active_uid, 0) or 0)
        guard_owner = owner
        params = owner if hasattr(owner, 'izom_propui_free_entries') else _izom_propui_free_find_params_for_entry(owner, None)
        if params is not None:
            guard_owner = params
        _context_guard_key = _izom_propui_free_suspend_list_context_updates(guard_owner)
        try:
            try:
                setattr(owner, active_attr, active_index)
                setattr(owner, active_uid_attr, active_uid)
                setattr(owner, anchor_attr, anchor_uid)
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
        finally:
            _izom_propui_free_resume_list_context_updates(guard_owner)
        _izom_propui_free_store_uid_list(owner, selected_attr, selected)
        return selected
    finally:
        _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.discard(selection_guard_key)


def _izom_propui_free_active_collection_item(owner, collection_name):
    state = _izom_propui_free_collection_state(owner, collection_name)
    collection = state.get('items', ())
    if not collection:
        return None
    active_attr, active_uid_attr, _selected_attr, _anchor_attr = _izom_propui_free_collection_selection_fields(collection_name)
    try:
        index = int(getattr(owner, active_attr, 0))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        index = 0
    if collection:
        index = max(0, min(index, len(collection) - 1))
    else:
        index = 0
    index_item = collection[index] if 0 <= index < len(collection) else None
    active_uid = str(getattr(owner, active_uid_attr, '') or '').strip()
    if active_uid:
        active_item = state.get('by_uid', {}).get(active_uid)
        if active_item is not None:
            return active_item
    return index_item

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
