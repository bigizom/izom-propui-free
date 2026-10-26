# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_value_labels_common_base import (
    _izom_propui_free_value_label_editor_context,
    izom_propui_free_log_recovered,
)
from .helper_cache_updates_invalidation import _izom_propui_free_schedule_runtime_entry_cache_invalidate
from .helper_selection_collections import (
    _izom_propui_free_bump_collection_revision,
    _izom_propui_free_set_collection_selection_direct,
)
from .helper_selection_common import (
    _izom_propui_free_set_last_editor_context,
    _izom_propui_free_tag_all_redraw,
    _izom_propui_free_uid_list_from_json,
)
from .helper_selection_context import _izom_propui_free_set_last_clicked_list_context


def _izom_propui_free_focus_value_label_editor(info, target_mode):
    params = info.get('params') if info else None
    if params is not None:
        context_name = _izom_propui_free_value_label_editor_context(target_mode)
        _izom_propui_free_set_last_editor_context(params, context_name)
        _izom_propui_free_set_last_clicked_list_context(params, context_name)
    return params


def _izom_propui_free_selected_value_label_uids(owner, collection_name):
    selected_uids = [
        str(uid or '').strip()
        for uid in _izom_propui_free_uid_list_from_json(getattr(owner, f"{collection_name}_selected_uids_json", '[]'))
        if str(uid or '').strip()
    ]
    if selected_uids:
        return selected_uids
    current_uid = str(getattr(owner, f"{collection_name}_active_uid", '') or '').strip()
    if current_uid:
        return [current_uid]
    collection = getattr(owner, collection_name, None)
    try:
        collection_len = len(collection) if collection is not None else 0
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        collection_len = 0
    if collection_len <= 0:
        return []
    try:
        active_index = max(0, min(int(getattr(owner, f"{collection_name}_active_index", 0) or 0), collection_len - 1))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        active_index = 0
    current_uid = str(getattr(collection[active_index], 'uid', '') or '').strip() if active_index >= 0 else ''
    return [current_uid] if current_uid else []


def _izom_propui_free_selected_value_label_indexes(collection, selected_uids):
    selected_uid_set = set(selected_uids)
    return [
        index for index, candidate in enumerate(collection)
        if str(getattr(candidate, 'uid', '') or '').strip() in selected_uid_set
    ]


def _izom_propui_free_active_value_label_index_direct(owner, collection_name, collection, selected_uids=None):
    try:
        collection_len = len(collection)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        collection_len = 0
    if collection_len <= 0:
        return -1
    active_uid = str(getattr(owner, f"{collection_name}_active_uid", '') or '').strip()
    try:
        active_index = max(0, min(int(getattr(owner, f"{collection_name}_active_index", 0) or 0), collection_len - 1))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        active_index = 0
    selected = [str(uid or '').strip() for uid in (selected_uids or []) if str(uid or '').strip()]
    if selected:
        target_uid = selected[-1]
        if str(getattr(collection[active_index], 'uid', '') or '').strip() == target_uid:
            return active_index
        for index, candidate in enumerate(collection):
            if str(getattr(candidate, 'uid', '') or '').strip() == target_uid:
                return index
        return -1
    if active_uid and str(getattr(collection[active_index], 'uid', '') or '').strip() == active_uid:
        return active_index
    target_uid = active_uid
    if target_uid:
        for index, candidate in enumerate(collection):
            if str(getattr(candidate, 'uid', '') or '').strip() == target_uid:
                return index
        return -1
    return active_index


def _izom_propui_free_selected_value_label_indexes_direct(owner, collection_name, collection, selected_uids):
    selected = [str(uid or '').strip() for uid in (selected_uids or []) if str(uid or '').strip()]
    if len(selected) == 1:
        index = _izom_propui_free_active_value_label_index_direct(owner, collection_name, collection, selected)
        if index >= 0 and str(getattr(collection[index], 'uid', '') or '').strip() == selected[0]:
            return [index]
    return _izom_propui_free_selected_value_label_indexes(collection, selected)


def _izom_propui_free_select_value_label_direct(owner, collection_name, collection, active_uid, active_index, *, selected_uids=None, anchor_uid=None):
    _izom_propui_free_set_collection_selection_direct(
        owner,
        collection_name,
        selected_uids if selected_uids is not None else ([active_uid] if active_uid else []),
        active_uid=active_uid,
        active_index=active_index,
        anchor_uid=anchor_uid if anchor_uid is not None else active_uid,
    )


def _izom_propui_free_finish_value_label_collection_mutation(owner, collection_name, collection, active_uid, active_index, *, selected_uids=None, anchor_uid=None, params=None):
    _izom_propui_free_bump_collection_revision(owner, collection_name)
    _izom_propui_free_select_value_label_direct(
        owner,
        collection_name,
        collection,
        str(active_uid or '').strip(),
        active_index,
        selected_uids=selected_uids,
        anchor_uid=anchor_uid,
    )
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)
    _izom_propui_free_tag_all_redraw()



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
