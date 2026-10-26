# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from ..core.cache_common import _izom_propui_free_pointer_guard_key
from .helper_cache_updates_entry_runtime import _izom_propui_free_entry_runtime_state_updated
from .helper_cache_updates_entry_params import (
    _izom_propui_free_context_bulk_entry_updates_suspended,
    _izom_propui_free_entry_runtime_update_callbacks_suspended,
    _izom_propui_free_find_params_for_entry,
)
from .helper_layout_entry_collapse import (
    _izom_propui_free_entry_collapsed,
    _izom_propui_free_toggle_entry_collapsed_and_focus,
)


def _izom_propui_free_entry_list_collapsed_get(entry):
    params = _izom_propui_free_find_params_for_entry(entry, bpy.context)
    if params is None:
        return False
    entry_uid = str(getattr(entry, 'uid', '') or '').strip()
    if not entry_uid:
        return False
    return _izom_propui_free_entry_collapsed(params, entry_uid)


def _izom_propui_free_entry_list_collapsed_set(entry, value):
    params = _izom_propui_free_find_params_for_entry(entry, bpy.context)
    if params is None:
        return
    entry_uid = str(getattr(entry, 'uid', '') or '').strip()
    if not entry_uid:
        return
    target_state = bool(value)
    current_state = _izom_propui_free_entry_collapsed(params, entry_uid)
    if target_state == current_state:
        return
    _izom_propui_free_toggle_entry_collapsed_and_focus(params, entry_uid)


IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSE_STATE_ITEMS = (
    ('EXPANDED', 'Expanded', 'Show this parent entry expanded in the Entry List', 1),
    ('COLLAPSED', 'Collapsed', 'Show this parent entry collapsed in the Entry List', 2),
)


_IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD = set()


def _izom_propui_free_model_entry_update_suspended(context):
    return (
        _izom_propui_free_entry_runtime_update_callbacks_suspended()
        or _izom_propui_free_context_bulk_entry_updates_suspended(context)
    )


def _izom_propui_free_use_soft_limits_updated(entry, context):
    if _izom_propui_free_model_entry_update_suspended(context):
        return
    guard_key = _izom_propui_free_pointer_guard_key(entry)
    if guard_key not in _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD and bool(getattr(entry, 'use_soft_limits', False)):
        _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD.add(guard_key)
        try:
            if bool(getattr(entry, 'slider', False)):
                entry.slider = False
        finally:
            _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD.discard(guard_key)
    _izom_propui_free_entry_runtime_state_updated(entry, context)


def _izom_propui_free_slider_updated(entry, context):
    if _izom_propui_free_model_entry_update_suspended(context):
        return
    guard_key = _izom_propui_free_pointer_guard_key(entry)
    if guard_key not in _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD and bool(getattr(entry, 'slider', False)):
        _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD.add(guard_key)
        try:
            if bool(getattr(entry, 'use_soft_limits', False)):
                entry.use_soft_limits = False
        finally:
            _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD.discard(guard_key)
    _izom_propui_free_entry_runtime_state_updated(entry, context)


def _izom_propui_free_entry_list_collapse_state_get(entry):
    return 2 if _izom_propui_free_entry_list_collapsed_get(entry) else 1


def _izom_propui_free_entry_list_collapse_state_set(entry, value):
    try:
        target_state = int(value)
    except (TypeError, ValueError):
        return
    if target_state not in {1, 2}:
        return
    params = _izom_propui_free_find_params_for_entry(entry, bpy.context)
    if params is None:
        return
    entry_uid = str(getattr(entry, 'uid', '') or '').strip()
    if not entry_uid:
        return
    target_collapsed = target_state == 2
    current_state = _izom_propui_free_entry_collapsed(params, entry_uid)
    if target_collapsed == current_state:
        return
    _izom_propui_free_toggle_entry_collapsed_and_focus(params, entry_uid)


def _izom_propui_free_clear_entry_model_update_session_caches():
    _IZOM_PROPUI_FREE_SLIDER_SOFT_LIMIT_UPDATE_GUARD.clear()


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
