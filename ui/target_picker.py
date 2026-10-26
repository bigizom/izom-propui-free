# SPDX-License-Identifier: GPL-3.0-or-later

import time

from ..core.targets import (
    izom_propui_free_resolve_owner_path,
)


_IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE = {}
_IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE_SECONDS = 8.0


def _izom_propui_free_clear_target_picker_session_caches():
    _IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE.clear()


def _izom_propui_free_target_path_status(path, *, max_age=None):
    path_text = str(path or '').strip()
    if not path_text:
        return {
            'exists': False,
            'label': 'None',
        }
    now = time.monotonic()
    try:
        age_limit = _IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE_SECONDS if max_age is None else max(0.0, float(max_age))
    except (TypeError, ValueError, OverflowError):
        age_limit = _IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE_SECONDS
    cached = _IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE.get(path_text)
    if cached is not None:
        try:
            cached_at = float(cached.get('cached_at', 0.0) or 0.0)
        except (TypeError, ValueError, OverflowError):
            cached_at = 0.0
        if now - cached_at <= age_limit:
            return dict(cached.get('status', {}) or {})

    owner = izom_propui_free_resolve_owner_path(path_text)
    if owner is None:
        label = path_text
    else:
        name = str(getattr(owner, 'name', '') or '').strip()
        type_name = type(owner).__name__
        label = f"{type_name}: {name}" if name else type_name
    status = {
        'exists': owner is not None,
        'label': label,
    }
    _IZOM_PROPUI_FREE_TARGET_PATH_STATUS_CACHE[path_text] = {
        'cached_at': now,
        'status': dict(status),
    }
    return status


def draw_izom_propui_free_target_context_buttons(
    layout,
    owner,
    prefix,
    *,
    path_attr='',
    entry_uid='',
    active_text='Set Active',
    selected_text='Set Selected',
):
    return


def draw_izom_propui_free_target_picker(
    layout,
    owner,
    prefix,
    *,
    path_attr='',
    label='Target',
    allow_default=False,
    entry_uid='',
    show_context_buttons=False,
):
    kind_attr = f"{prefix}_kind"
    object_attr = f"{prefix}_object"
    kind = str(getattr(owner, kind_attr, 'DEFAULT' if allow_default else 'OBJECT') or '').strip().upper()

    column = layout.column(align=True)
    if hasattr(owner, kind_attr):
        try:
            setattr(owner, kind_attr, 'OBJECT' if not allow_default else 'DEFAULT')
        except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError):
            pass

    if kind == 'DEFAULT' and allow_default:
        path = str(getattr(owner, path_attr, '') or '').strip() if path_attr else ''
        if path:
            status = _izom_propui_free_target_path_status(path)
            icon = 'CHECKMARK' if status.get('exists') else 'ERROR'
            column.label(text=f"Saved Override: {status.get('label', path)}", icon=icon)
        else:
            column.label(text="Using Output Setup property storage.")
    else:
        column.prop(owner, object_attr, text="Object")

    if path_attr:
        path = str(getattr(owner, path_attr, '') or '').strip()
        if kind == 'DEFAULT' and allow_default:
            return
        status = _izom_propui_free_target_path_status(path)
        icon = 'CHECKMARK' if status.get('exists') else 'ERROR'
        column.label(text=f"Resolved: {status.get('label', path or 'None')}", icon=icon)
    if show_context_buttons:
        draw_izom_propui_free_target_context_buttons(
            column,
            owner,
            prefix,
            path_attr=path_attr,
            entry_uid=entry_uid,
        )
