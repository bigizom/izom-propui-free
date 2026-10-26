# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_layout_selection import (
    _izom_propui_free_set_last_clicked_list_context,
    _izom_propui_free_set_last_editor_context,
    izom_propui_free_cached_entry_navigation_bundle,
)
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_cache_fields
from .helper_selection_common import (
    _izom_propui_free_store_uid_list,
    _izom_propui_free_tag_all_redraw,
)


def _izom_propui_free_active_entry_uid(*args, **kwargs):
    from .helper_selection_entries import _izom_propui_free_active_entry_uid as active_entry_uid

    return active_entry_uid(*args, **kwargs)


def _izom_propui_free_set_entry_selection(*args, **kwargs):
    from .helper_selection_entries import _izom_propui_free_set_entry_selection as set_entry_selection

    return set_entry_selection(*args, **kwargs)



def _izom_propui_free_entry_collapsed_uids(params):
    if params is None:
        return []
    return list(izom_propui_free_cached_entry_navigation_bundle(params).get('entry_collapsed_uids', []))


def _izom_propui_free_set_entry_collapsed_uids(params, entry_uids):
    if params is None:
        return []
    stored = _izom_propui_free_store_uid_list(params, 'izom_propui_free_entry_collapsed_uids_json', entry_uids)
    _izom_propui_free_invalidate_cache_fields(params, 'entry_collapsed_uids')
    return stored


def _izom_propui_free_entry_collapsed(params, entry_uid):
    target_uid = str(entry_uid or '').strip()
    return bool(target_uid) and target_uid in izom_propui_free_cached_entry_navigation_bundle(params).get('entry_collapsed_uid_set', set())


def _izom_propui_free_toggle_entry_collapsed(params, entry_uid):
    target_uid = str(entry_uid or '').strip()
    if not target_uid:
        return False
    collapsed = _izom_propui_free_entry_collapsed_uids(params)
    collapsed_set = set(collapsed)
    if target_uid in collapsed_set:
        collapsed = [uid for uid in collapsed if uid != target_uid]
        new_state = False
    else:
        collapsed.append(target_uid)
        new_state = True
    _izom_propui_free_set_entry_collapsed_uids(params, collapsed)
    return new_state


def _izom_propui_free_focus_visible_entry_list_uid(params, *, preferred_uid='', fallback_uid=''):
    if params is None:
        return ''

    state_bundle = izom_propui_free_cached_entry_navigation_bundle(params)
    entry_draw_state = state_bundle.get('entry_draw_state', {}) or {}
    visible_order_attr = 'visible_entry_list_uids' if bool(getattr(params, 'izom_propui_free_show_entry_tree_hints', True)) else 'visible_hierarchy_uids'
    visible_set_attr = 'visible_entry_list_uid_set' if visible_order_attr == 'visible_entry_list_uids' else 'visible_hierarchy_uid_set'
    visible_order = [
        str(uid or '').strip()
        for uid in (entry_draw_state.get(visible_order_attr, []) or [])
        if str(uid or '').strip()
    ]
    if not visible_order:
        return ''

    visible_uid_set = entry_draw_state.get(visible_set_attr)
    if visible_uid_set is None:
        visible_uid_set = set(visible_order)
    else:
        visible_uid_set = {
            str(uid or '').strip()
            for uid in visible_uid_set
            if str(uid or '').strip()
        }

    focus_uid = ''
    for candidate in (preferred_uid, fallback_uid):
        candidate_uid = str(candidate or '').strip()
        if candidate_uid and candidate_uid in visible_uid_set:
            focus_uid = candidate_uid
            break
    if not focus_uid:
        focus_uid = visible_order[0]

    current_active_uid = _izom_propui_free_active_entry_uid(
        params,
        editor_context='HIERARCHY',
        persist=False,
    )
    if current_active_uid == focus_uid:
        return focus_uid

    _izom_propui_free_set_entry_selection(
        params,
        [focus_uid],
        active_uid=focus_uid,
        anchor_uid=focus_uid,
        editor_context='HIERARCHY',
        update_list_context=False,
    )
    return focus_uid


def _izom_propui_free_toggle_entry_collapsed_and_focus(params, entry_uid):
    if params is None:
        return False

    target_uid = str(entry_uid or '').strip()
    if not target_uid:
        return False

    state_bundle = izom_propui_free_cached_entry_navigation_bundle(params)
    tree_state = state_bundle.get('tree_state', {}) or {}
    if target_uid not in (tree_state.get('children_by_uid', {}) or {}):
        return False

    active_uid = _izom_propui_free_active_entry_uid(
        params,
        editor_context='HIERARCHY',
        persist=False,
    )
    _izom_propui_free_toggle_entry_collapsed(params, target_uid)
    if active_uid != target_uid:
        _izom_propui_free_focus_visible_entry_list_uid(
            params,
            preferred_uid=target_uid,
            fallback_uid=target_uid,
        )
    _izom_propui_free_set_last_editor_context(params, 'HIERARCHY')
    _izom_propui_free_set_last_clicked_list_context(params, 'ENTRY_LIST')
    _izom_propui_free_tag_all_redraw()
    return True

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
