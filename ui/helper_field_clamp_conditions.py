# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_field_clamp_compare import (
    _izom_propui_free_find_params_for_entry,
    _izom_propui_free_pointer_guard_key,
    _izom_propui_free_visibility_compare_info,
    izom_propui_free_log_recovered,
)
from ..core.runtime_ui_kwargs import (
    _izom_propui_free_clamp_float,
    _izom_propui_free_clamp_int,
)
from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD,
)
from .helper_field_clamp_common import _izom_propui_free_snap_editor_float_value_for_params


_IZOM_PROPUI_FREE_CONDITION_CLAMP_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_visibility_match_guard_key(entry, field_name):
    return (_izom_propui_free_pointer_guard_key(entry), str(field_name))


def _izom_propui_free_clamp_visibility_match_float(entry, context=None, *, params=None, parent=None, info=None):
    guard_key = _izom_propui_free_visibility_match_guard_key(entry, 'visibility_match_float')
    if guard_key in _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD:
        return

    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, context)
    if info is None:
        info = _izom_propui_free_visibility_compare_info(params, entry, parent=parent)
    if not info or info.get('parent_prop_type') != 'FLOAT':
        return

    min_value = info.get('min_value')
    max_value = info.get('max_value')
    base_value = float(min_value) if min_value is not None else 0.0
    default_value = float(min_value) if min_value is not None else 0.0
    try:
        current_value = float(getattr(entry, 'visibility_match_float', default_value))
    except _IZOM_PROPUI_FREE_CONDITION_CLAMP_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current_value = default_value

    snapped_value = _izom_propui_free_snap_editor_float_value_for_params(params, current_value, base=base_value)
    clamped_value = _izom_propui_free_clamp_float(
        snapped_value,
        default=default_value,
        min_value=min_value,
        max_value=max_value,
    )
    if abs(float(current_value) - float(clamped_value)) <= 1e-6:
        return

    _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.add(guard_key)
    try:
        entry.visibility_match_float = float(clamped_value)
    finally:
        _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_clamp_visibility_match_int(entry, context=None, *, params=None, parent=None, info=None):
    guard_key = _izom_propui_free_visibility_match_guard_key(entry, 'visibility_match_int')
    if guard_key in _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD:
        return

    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, context)
    if info is None:
        info = _izom_propui_free_visibility_compare_info(params, entry, parent=parent)
    if not info or info.get('parent_prop_type') != 'INT':
        return

    min_value = info.get('min_value')
    max_value = info.get('max_value')
    default_value = int(min_value) if min_value is not None else 0
    try:
        current_value = int(getattr(entry, 'visibility_match_int', default_value) or default_value)
    except _IZOM_PROPUI_FREE_CONDITION_CLAMP_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current_value = default_value

    clamped_value = _izom_propui_free_clamp_int(
        current_value,
        default=default_value,
        min_value=min_value,
        max_value=max_value,
    )
    if int(current_value) == int(clamped_value):
        return

    _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.add(guard_key)
    try:
        entry.visibility_match_int = int(clamped_value)
    finally:
        _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_clamp_visibility_range_max_float(entry, context=None, *, params=None, parent=None, info=None):
    guard_key = _izom_propui_free_visibility_match_guard_key(entry, 'visibility_range_max_float')
    if guard_key in _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD:
        return

    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, context)
    if info is None:
        info = _izom_propui_free_visibility_compare_info(params, entry, parent=parent)
    if not info or info.get('parent_prop_type') != 'FLOAT':
        return

    min_value = info.get('min_value')
    max_value = info.get('max_value')
    default_value = float(max_value) if max_value is not None else 1.0
    try:
        current_value = float(getattr(entry, 'visibility_range_max_float', default_value))
    except _IZOM_PROPUI_FREE_CONDITION_CLAMP_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current_value = default_value

    snapped_value = _izom_propui_free_snap_editor_float_value_for_params(params, current_value, base=float(min_value) if min_value is not None else 0.0)
    clamped_value = _izom_propui_free_clamp_float(
        snapped_value,
        default=default_value,
        min_value=min_value,
        max_value=max_value,
    )
    if abs(float(current_value) - float(clamped_value)) <= 1e-6:
        return

    _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.add(guard_key)
    try:
        entry.visibility_range_max_float = float(clamped_value)
    finally:
        _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_clamp_visibility_range_max_int(entry, context=None, *, params=None, parent=None, info=None):
    guard_key = _izom_propui_free_visibility_match_guard_key(entry, 'visibility_range_max_int')
    if guard_key in _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD:
        return

    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, context)
    if info is None:
        info = _izom_propui_free_visibility_compare_info(params, entry, parent=parent)
    if not info or info.get('parent_prop_type') != 'INT':
        return

    min_value = info.get('min_value')
    max_value = info.get('max_value')
    default_value = int(max_value) if max_value is not None else 5
    try:
        current_value = int(getattr(entry, 'visibility_range_max_int', default_value) or default_value)
    except _IZOM_PROPUI_FREE_CONDITION_CLAMP_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current_value = default_value

    clamped_value = _izom_propui_free_clamp_int(
        current_value,
        default=default_value,
        min_value=min_value,
        max_value=max_value,
    )
    if int(current_value) == int(clamped_value):
        return

    _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.add(guard_key)
    try:
        entry.visibility_range_max_int = int(clamped_value)
    finally:
        _IZOM_PROPUI_FREE_VISIBILITY_MATCH_UPDATE_GUARD.discard(guard_key)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
