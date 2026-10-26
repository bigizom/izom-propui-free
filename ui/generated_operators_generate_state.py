# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
from .helpers import (
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_set_attr_if_changed,
    _izom_propui_free_suspend_list_context_updates,
)

_IZOM_PROPUI_FREE_GENERATE_EDITOR_STATE_ATTRS = (
    'izom_propui_free_active_index',
    'izom_propui_free_active_uid',
    'izom_propui_free_selected_uids_json',
    'izom_propui_free_selection_anchor_uid',
    'izom_propui_free_layout_active_index',
    'izom_propui_free_layout_active_uid',
    'izom_propui_free_layout_selected_uids_json',
    'izom_propui_free_layout_selection_anchor_uid',
    'izom_propui_free_layout_view_active_index',
    'izom_propui_free_layout_view_active_uid',
    'izom_propui_free_layout_view_selected_uids_json',
    'izom_propui_free_layout_view_selection_anchor_uid',
    'izom_propui_free_last_editor_context',
    'izom_propui_free_last_entry_editor_context',
    'izom_propui_free_last_clicked_list_context',
)

def _izom_propui_free_capture_generate_editor_state(params):
    state = {'attrs': {}}
    if params is None:
        return state
    for attr_name in _IZOM_PROPUI_FREE_GENERATE_EDITOR_STATE_ATTRS:
        if not hasattr(params, attr_name):
            continue
        try:
            state['attrs'][attr_name] = getattr(params, attr_name)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
    return state


def _izom_propui_free_restore_generate_editor_state(params, state):
    if params is None or not state:
        return
    _izom_propui_free_suspend_list_context_updates(params)
    try:
        for attr_name in _IZOM_PROPUI_FREE_GENERATE_EDITOR_STATE_ATTRS:
            attrs = state.get('attrs', {})
            if attr_name not in attrs or not hasattr(params, attr_name):
                continue
            _izom_propui_free_set_attr_if_changed(params, attr_name, attrs[attr_name])
    finally:
        _izom_propui_free_resume_list_context_updates(params)



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
