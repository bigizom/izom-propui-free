# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .helper_selection_common import (
    izom_propui_free_log_recovered,
)
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD



def _izom_propui_free_normalize_clicked_list_context(list_context):
    mode = str(list_context or '').strip().upper()
    if mode in {'DISABLED', 'ENTRY_LIST', 'GL_LIST', 'VALUE_LABEL_SELF', 'VALUE_LABEL_BUCKET_SOURCE'}:
        return mode
    if mode == 'HIERARCHY':
        return 'ENTRY_LIST'
    if mode == 'LAYOUT':
        return 'GL_LIST'
    return 'ENTRY_LIST'


def _izom_propui_free_clicked_list_context_for_editor(editor_context):
    mode = str(editor_context or '').strip().upper()
    if mode == 'LAYOUT':
        return 'GL_LIST'
    if mode == 'HIERARCHY':
        return 'ENTRY_LIST'
    if mode in {'VALUE_LABEL_SELF', 'VALUE_LABEL_BUCKET_SOURCE'}:
        return mode
    return 'ENTRY_LIST'


def _izom_propui_free_set_last_clicked_list_context(params, list_context):
    if params is None:
        return 'ENTRY_LIST'
    mode = _izom_propui_free_normalize_clicked_list_context(list_context)
    try:
        params.izom_propui_free_last_clicked_list_context = mode
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    if mode == 'ENTRY_LIST':
        try:
            params.izom_propui_free_last_entry_editor_context = 'HIERARCHY'
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    elif mode == 'GL_LIST':
        try:
            params.izom_propui_free_last_entry_editor_context = 'LAYOUT'
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    return mode


def _izom_propui_free_list_context_guard_key(owner):
    try:
        return int(owner.as_pointer())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return id(owner)


def _izom_propui_free_suspend_list_context_updates(owner):
    if owner is None:
        return None
    key = _izom_propui_free_list_context_guard_key(owner)
    _IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD[key] = int(_IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD.get(key, 0) or 0) + 1
    return key


def _izom_propui_free_resume_list_context_updates(owner):
    if owner is None:
        return
    key = _izom_propui_free_list_context_guard_key(owner)
    count = int(_IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD.get(key, 0) or 0)
    if count <= 1:
        _IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD.pop(key, None)
    else:
        _IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD[key] = count - 1


def _izom_propui_free_list_context_updates_suspended(owner):
    if owner is None:
        return False
    return int(_IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD.get(_izom_propui_free_list_context_guard_key(owner), 0) or 0) > 0

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
