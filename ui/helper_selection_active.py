# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_selection_entries import (
    _izom_propui_free_active_entry_uid,
    _izom_propui_free_editor_selection_fields,
    _izom_propui_free_sync_entry_selection,
)
from .helper_selection_collections import (
    _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD,
    _izom_propui_free_collection_active_index_guard_key,
    _izom_propui_free_find_params_for_entry,
    _izom_propui_free_pointer_guard_key,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
    _izom_propui_free_sync_collection_selection,
)
from ..core.context import izom_propui_free_context_params
from .helper_cache_updates_entry_params import (
    _izom_propui_free_bulk_entry_updates_suspended,
)
from .helper_selection_common import (
    _izom_propui_free_entry_by_uid,
    _izom_propui_free_set_attr_if_changed,
    _izom_propui_free_set_last_editor_context,
    _izom_propui_free_smart_expand_selected_entry_sections,
)
from .helper_selection_context import (
    _izom_propui_free_clicked_list_context_for_editor,
    _izom_propui_free_list_context_updates_suspended,
    _izom_propui_free_set_last_clicked_list_context,
)



def _izom_propui_free_active_entry(context_or_params):
    params = (
        context_or_params
        if hasattr(context_or_params, 'izom_propui_free_entries')
        else izom_propui_free_context_params(context_or_params)
    )
    if params is None:
        return None
    entries = getattr(params, 'izom_propui_free_entries', None)
    if not entries:
        return None
    active_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY', persist=False)
    entry = _izom_propui_free_entry_by_uid(params, active_uid)
    if entry is not None:
        return entry
    index = max(0, min(getattr(params, 'izom_propui_free_active_index', 0), len(entries) - 1))
    return entries[index] if 0 <= index < len(entries) else None


def _izom_propui_free_active_index_guard_key(owner, editor_context='HIERARCHY'):
    return ('active_index', str(editor_context or 'HIERARCHY').strip().upper(), _izom_propui_free_pointer_guard_key(owner))


def _izom_propui_free_sync_entry_active_indices(params, *, source='HIERARCHY'):
    mode = 'LAYOUT' if str(source or '').strip().upper() == 'LAYOUT' else 'HIERARCHY'
    guard_key = _izom_propui_free_active_index_guard_key(params, mode)
    if guard_key in _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD:
        return

    entries = list(getattr(params, 'izom_propui_free_entries', []) or [])
    if not entries:
        _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.add(guard_key)
        try:
            _izom_propui_free_suspend_list_context_updates(params)
            try:
                active_attr, active_uid_attr, _selected_attr, _anchor_attr = _izom_propui_free_editor_selection_fields(mode)
                _izom_propui_free_set_attr_if_changed(params, active_attr, 0)
                _izom_propui_free_set_attr_if_changed(params, active_uid_attr, '')
                if mode == 'HIERARCHY' and hasattr(params, 'izom_propui_free_layout_active_index'):
                    _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_index', 0)
                if mode == 'HIERARCHY' and hasattr(params, 'izom_propui_free_layout_active_uid'):
                    _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_uid', '')
            finally:
                _izom_propui_free_resume_list_context_updates(params)
            if mode == 'HIERARCHY':
                _izom_propui_free_smart_expand_selected_entry_sections(params, '')
        finally:
            _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.discard(guard_key)
        return

    _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.add(guard_key)
    try:
        if mode == 'LAYOUT':
            from .helper_layout import _izom_propui_free_sync_layout_selection

            _izom_propui_free_sync_layout_selection(
                params,
                preferred_active_index=int(getattr(params, 'izom_propui_free_layout_active_index', 0) or 0),
            )
        else:
            active_attr, _active_uid_attr, _selected_attr, _anchor_attr = _izom_propui_free_editor_selection_fields(mode)
            _izom_propui_free_sync_entry_selection(
                params,
                preferred_active_index=int(getattr(params, active_attr, 0) or 0),
                editor_context=mode,
            )
        if not _izom_propui_free_list_context_updates_suspended(params):
            _izom_propui_free_set_last_editor_context(params, mode)
            _izom_propui_free_set_last_clicked_list_context(params, _izom_propui_free_clicked_list_context_for_editor(mode))
    finally:
        _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_active_index_updated(params, _context):
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    if _izom_propui_free_list_context_updates_suspended(params):
        return
    _izom_propui_free_sync_entry_active_indices(params, source='HIERARCHY')


def _izom_propui_free_layout_active_index_updated(params, _context):
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    if _izom_propui_free_list_context_updates_suspended(params):
        return
    _izom_propui_free_sync_entry_active_indices(params, source='LAYOUT')


def _izom_propui_free_layout_view_active_index_updated(params, _context):
    if params is None:
        return
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    if _izom_propui_free_list_context_updates_suspended(params):
        return
    from .operators_layout_support import _izom_propui_free_sync_layout_view_selection

    try:
        index = int(getattr(params, 'izom_propui_free_layout_view_active_index', 0) or 0)
    except (AttributeError, TypeError, ValueError):
        index = 0
    _izom_propui_free_sync_layout_view_selection(params, preferred_active_index=index)
    if not _izom_propui_free_list_context_updates_suspended(params):
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
    _izom_propui_free_set_last_clicked_list_context(params, 'GL_LIST')


def _izom_propui_free_sync_value_label_active_index(owner, collection_name, context_name):
    if _izom_propui_free_collection_active_index_guard_key(owner, collection_name) in _IZOM_PROPUI_FREE_ACTIVE_INDEX_UPDATE_GUARD:
        return
    params = _izom_propui_free_find_params_for_entry(owner, None)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_sync_collection_selection(
        owner,
        collection_name,
        preferred_active_index=int(getattr(owner, f"{collection_name}_active_index", 0) or 0),
    )
    if params is not None and not _izom_propui_free_list_context_updates_suspended(params):
        _izom_propui_free_set_last_editor_context(params, context_name)
        _izom_propui_free_set_last_clicked_list_context(params, context_name)


def _izom_propui_free_entry_value_labels_active_index_updated(owner, _context):
    _izom_propui_free_sync_value_label_active_index(owner, 'value_labels', 'VALUE_LABEL_SELF')

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
