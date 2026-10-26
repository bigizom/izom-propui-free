# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_layout_live_core import (
    _izom_propui_free_json_dumps,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
    _izom_propui_free_uid_list_from_json,
)
from .helper_layout_view import (
    _izom_propui_free_layout_view_state,
    _izom_propui_free_set_layout_view_selection,
)
from .helper_selection_common import _izom_propui_free_set_attr_if_changed
from .operators_layout_view import _izom_propui_free_sync_layout_view_selection



def _izom_propui_free_capture_layout_view_selection(params, *, validate=True):
    if params is None:
        return {'active_uid': '', 'active_index': 0, 'selected_uids': [], 'anchor_uid': ''}
    try:
        current_index = int(getattr(params, 'izom_propui_free_layout_view_active_index', 0) or 0)
    except (TypeError, ValueError):
        current_index = 0
    if bool(validate):
        _izom_propui_free_sync_layout_view_selection(params, preferred_active_index=current_index)
    return {
        'active_uid': str(getattr(params, 'izom_propui_free_layout_view_active_uid', '') or '').strip(),
        'active_index': current_index,
        'selected_uids': _izom_propui_free_uid_list_from_json(
            getattr(params, 'izom_propui_free_layout_view_selected_uids_json', '[]')
        ),
        'anchor_uid': str(getattr(params, 'izom_propui_free_layout_view_selection_anchor_uid', '') or '').strip(),
    }

def _izom_propui_free_restore_layout_view_selection(params, state):
    if params is None:
        return
    state = dict(state or {})
    active_uid = str(state.get('active_uid', '') or '').strip()
    try:
        active_index = int(state.get('active_index', 0) or 0)
    except (TypeError, ValueError):
        active_index = 0
    selected_uids = [str(uid or '').strip() for uid in state.get('selected_uids', []) if str(uid or '').strip()]
    anchor_uid = str(state.get('anchor_uid', '') or '').strip()
    if not active_uid and not selected_uids and not anchor_uid:
        return
    if not active_uid and hasattr(params, 'izom_propui_free_layout_view_items'):
        raw_uids = _izom_propui_free_layout_view_state(params).get('raw_uids', ())
        if raw_uids:
            active_index = max(0, min(active_index, len(raw_uids) - 1))
            active_uid = str(raw_uids[active_index] or '').strip()
    _izom_propui_free_set_layout_view_selection(
        params,
        selected_uids,
        active_uid=active_uid,
        anchor_uid=anchor_uid,
        update_list_context=False,
    )

def _izom_propui_free_restore_layout_view_selection_direct(params, state):
    if params is None:
        return False
    view_collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    layout_collection = getattr(params, 'izom_propui_free_layout_items', None)
    if view_collection is None:
        return False
    state = dict(state or {})
    active_uid = str(state.get('active_uid', '') or '').strip()
    selected_uids = [
        str(uid or '').strip()
        for uid in (state.get('selected_uids', []) or [])
        if str(uid or '').strip()
    ]
    anchor_uid = str(state.get('anchor_uid', '') or '').strip()
    if not active_uid and not selected_uids and not anchor_uid:
        return True
    try:
        active_index = int(state.get('active_index', 0) or 0)
    except (TypeError, ValueError):
        active_index = 0

    selected_uid_set = set(selected_uids)
    found_selected_uids = set()
    active_item = None
    if active_uid and 0 <= active_index < len(view_collection):
        candidate = view_collection[active_index]
        if str(getattr(candidate, 'uid', '') or '').strip() == active_uid:
            active_item = candidate
            found_selected_uids.add(active_uid)

    if active_item is None or selected_uid_set - found_selected_uids:
        active_item = None
        for index, item in enumerate(view_collection):
            uid = str(getattr(item, 'uid', '') or '').strip()
            if not uid:
                continue
            if uid == active_uid:
                active_item = item
                active_index = index
            if uid in selected_uid_set:
                found_selected_uids.add(uid)
            if (
                (not active_uid or active_item is not None)
                and not (selected_uid_set - found_selected_uids)
            ):
                break

    if active_uid and active_item is None:
        return False
    if selected_uid_set - found_selected_uids:
        return False
    if not selected_uids and active_uid:
        selected_uids = [active_uid]
    if anchor_uid and anchor_uid not in found_selected_uids and anchor_uid != active_uid:
        return False

    layout_uid = ''
    if active_item is not None:
        kind = str(getattr(active_item, 'kind', '') or '').strip()
        if kind == 'ENTRY_ITEM':
            layout_uid = str(getattr(active_item, 'layout_uid', '') or '').strip()
        elif kind == 'ROW_HEADER':
            row_member_uids = _izom_propui_free_uid_list_from_json(
                getattr(active_item, 'row_member_uids_json', '[]')
            )
            layout_uid = row_member_uids[0] if row_member_uids else ''

    layout_index = -1
    if layout_uid and layout_collection is not None:
        for index, item in enumerate(layout_collection):
            if str(getattr(item, 'uid', '') or '').strip() == layout_uid:
                layout_index = index
                break
        if layout_index < 0:
            return False

    guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_active_index', max(0, active_index))
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_active_uid', active_uid)
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_selected_uids_json', _izom_propui_free_json_dumps(selected_uids))
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_selection_anchor_uid', anchor_uid or active_uid)
        if layout_uid:
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_index', max(0, layout_index))
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_uid', layout_uid)
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selected_uids_json', _izom_propui_free_json_dumps([layout_uid]))
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selection_anchor_uid', layout_uid)
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    return True


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
