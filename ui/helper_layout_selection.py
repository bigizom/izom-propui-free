# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_layout_lookup import (
    _izom_propui_free_layout_item_by_uid,
    _izom_propui_free_layout_item_uid_order,
    _izom_propui_free_layout_visible_entry_uids,
    _izom_propui_free_set_attr_if_changed,
    izom_propui_free_cached_layout_bundle,
    izom_propui_free_log_recovered,
)
from ..core.cache_state import izom_propui_free_cached_entry_navigation_bundle
from ..core.snapshot_layout_ensure import izom_propui_free_ensure_layout_items
from .helper_selection_common import (
    _izom_propui_free_json_dumps,
    _izom_propui_free_set_last_editor_context,
    _izom_propui_free_uid_list_from_json,
)
from .helper_selection_context import (
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_set_last_clicked_list_context,
    _izom_propui_free_suspend_list_context_updates,
)



def _izom_propui_free_hierarchy_visible_uid_order(params):
    if params is None:
        return []
    return list(izom_propui_free_cached_entry_navigation_bundle(params).get('entry_draw_state', {}).get('visible_hierarchy_uids', []))


def _izom_propui_free_layout_uid_order(params):
    return _izom_propui_free_layout_visible_entry_uids(params)


def _izom_propui_free_entry_order_for_editor(params, editor_context='HIERARCHY'):
    mode = str(editor_context or 'HIERARCHY')
    if mode == 'LAYOUT':
        return _izom_propui_free_layout_uid_order(params)
    return _izom_propui_free_hierarchy_visible_uid_order(params)


def _izom_propui_free_sync_layout_selection(params, *, preferred_active_uid=None, preferred_active_index=None, persist=True):
    if params is None:
        return []
    collection = getattr(params, 'izom_propui_free_layout_items', None)
    try:
        collection_len = len(collection) if collection is not None else 0
    except (TypeError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        collection_len = 0
    state_bundle = izom_propui_free_cached_layout_bundle(params)
    layout_lookup = state_bundle.get('layout_item_lookup', {}) or {}
    order = list(layout_lookup.get('ordered_uids', ()))
    if collection_len <= 0 or not order:
        if persist:
            guard_key = _izom_propui_free_suspend_list_context_updates(params)
            try:
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_index', 0)
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_uid', '')
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selected_uids_json', '[]')
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selection_anchor_uid', '')
            finally:
                _izom_propui_free_resume_list_context_updates(params)
        return []

    visible_order = _izom_propui_free_layout_item_uid_order(params, visible_only=True)
    available_order = visible_order or order
    plain_index_selection = preferred_active_index is not None and preferred_active_uid is None
    selected = _izom_propui_free_uid_list_from_json(getattr(params, 'izom_propui_free_layout_selected_uids_json', '[]'))
    selected = [uid for uid in selected if uid in available_order]
    target_uid = str(preferred_active_uid or '').strip()
    if not target_uid and preferred_active_index is not None:
        try:
            index = max(0, min(int(preferred_active_index), collection_len - 1))
        except (TypeError, ValueError, OverflowError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            index = 0
        target_uid = order[index] if 0 <= index < len(order) else ''
    if not target_uid:
        target_uid = str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
    if not target_uid:
        try:
            index = max(0, min(int(getattr(params, 'izom_propui_free_layout_active_index', 0) or 0), collection_len - 1))
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            index = 0
        target_uid = order[index] if 0 <= index < len(order) else ''

    if target_uid not in available_order:
        target_uid = selected[0] if selected else (available_order[0] if available_order else '')
    if plain_index_selection and target_uid:
        selected = [target_uid]
    elif not selected and target_uid:
        selected = [target_uid]
    elif target_uid and target_uid not in selected:
        selected = [target_uid]

    active_index = int(layout_lookup.get('index_by_uid', {}).get(target_uid, 0) or 0)
    anchor_uid = str(getattr(params, 'izom_propui_free_layout_selection_anchor_uid', '') or '').strip()
    if plain_index_selection and target_uid:
        anchor_uid = target_uid
    if anchor_uid not in available_order:
        anchor_uid = selected[0] if selected else target_uid
    if persist:
        encoded_selected = _izom_propui_free_json_dumps(selected)
        guard_key = _izom_propui_free_suspend_list_context_updates(params)
        try:
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_index', active_index)
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_uid', target_uid)
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selected_uids_json', encoded_selected)
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selection_anchor_uid', anchor_uid)
        finally:
            _izom_propui_free_resume_list_context_updates(params)
    return selected


def _izom_propui_free_active_layout_item(params):
    if params is None:
        return None
    selected = _izom_propui_free_sync_layout_selection(params, persist=False)
    state_bundle = izom_propui_free_cached_layout_bundle(params)
    layout_lookup = state_bundle.get('layout_item_lookup', {}) or {}
    by_uid = layout_lookup.get('by_uid', {}) or {}
    order = tuple(layout_lookup.get('ordered_uids', ()))
    if not order:
        return None
    active_uid = str(getattr(params, 'izom_propui_free_layout_active_uid', '') or '').strip()
    available = set(order)
    if active_uid not in available:
        active_uid = selected[-1] if selected else ''
    if active_uid:
        item = by_uid.get(active_uid)
        if item is not None:
            return item
    try:
        index = max(0, min(int(getattr(params, 'izom_propui_free_layout_active_index', 0) or 0), len(order) - 1))
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        index = 0
    fallback_uid = order[index] if 0 <= index < len(order) else ''
    return by_uid.get(fallback_uid)


def _izom_propui_free_active_layout_item_uid(params):
    item = _izom_propui_free_active_layout_item(params)
    return str(getattr(item, 'uid', '') or '').strip() if item is not None else ''


def _izom_propui_free_active_layout_entry_uid(params):
    active_uid = _izom_propui_free_active_layout_item_uid(params)
    item = _izom_propui_free_layout_item_by_uid(params, active_uid)
    return str(getattr(item, 'entry_uid', '') or '').strip() if item is not None else ''


def _izom_propui_free_selected_layout_item_uids(params):
    return _izom_propui_free_sync_layout_selection(params)


def _izom_propui_free_set_layout_selection(params, selected_item_uids, *, active_uid=None, anchor_uid=None, update_list_context=False):
    if params is None:
        return []
    izom_propui_free_ensure_layout_items(params)
    available_order = _izom_propui_free_layout_item_uid_order(params, visible_only=True)
    if not available_order:
        available_order = _izom_propui_free_layout_item_uid_order(params, visible_only=False)
    available = set(available_order)

    cleaned = []
    seen = set()
    for item_uid in selected_item_uids or []:
        uid = str(item_uid or '').strip()
        if not uid or uid in seen or uid not in available:
            continue
        seen.add(uid)
        cleaned.append(uid)

    target_active = str(active_uid or '').strip()
    if target_active not in available:
        target_active = cleaned[-1] if cleaned else (available_order[0] if available_order else '')
    if not cleaned and target_active:
        cleaned = [target_active]

    target_anchor = str(anchor_uid or '').strip()
    if target_anchor not in available:
        target_anchor = cleaned[0] if cleaned else target_active

    guard_key = None
    if not update_list_context:
        guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        try:
            params.izom_propui_free_layout_active_uid = target_active
            params.izom_propui_free_layout_selected_uids_json = _izom_propui_free_json_dumps(cleaned)
            params.izom_propui_free_layout_selection_anchor_uid = target_anchor
        except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
        _izom_propui_free_sync_layout_selection(params, preferred_active_uid=target_active or None)
        try:
            params.izom_propui_free_layout_selected_uids_json = _izom_propui_free_json_dumps(cleaned)
            params.izom_propui_free_layout_selection_anchor_uid = target_anchor
        except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    if update_list_context:
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        _izom_propui_free_set_last_clicked_list_context(params, 'GL_LIST')
    return cleaned

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
