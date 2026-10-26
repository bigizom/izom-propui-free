# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_field_clamp_conditions import (
    _izom_propui_free_clamp_float,
    _izom_propui_free_clamp_int,
    _izom_propui_free_find_params_for_entry,
    _izom_propui_free_pointer_guard_key,
    _izom_propui_free_snap_editor_float_value_for_params,
    izom_propui_free_log_recovered,
)
from ..core.value_labels_common import _izom_propui_free_is_numeric_type
from ..core.value_labels_thresholds import (
    _izom_propui_free_normalize_editor_float_decimals,
    _izom_propui_free_snap_editor_float_value,
)
from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD,
    _IZOM_PROPUI_FREE_EDITOR_SETTINGS_UPDATE_GUARD,
    _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD,
)
from .helper_cache_updates_entry_params import _izom_propui_free_bulk_entry_updates_suspended
from .helper_cache_updates_invalidation import (
    _izom_propui_free_invalidate_runtime_entry_cache,
    _izom_propui_free_schedule_runtime_entry_cache_invalidate,
)
from .helper_field_clamp_common import (
    _izom_propui_free_editor_float_settings,
    _izom_propui_free_entry_field_update_suspended,
)




def _izom_propui_free_editor_float_proxy_name(field_name, params=None):
    if params is None:
        decimals = _izom_propui_free_normalize_editor_float_decimals(3)
    else:
        decimals, _step = _izom_propui_free_editor_float_settings(params)
    if int(decimals) <= 0:
        return f"{str(field_name)}_editor_i"
    return f"{str(field_name)}_editor_p{int(decimals)}"


def _izom_propui_free_draw_editor_float_prop(layout, item, field_name, params=None, *, text=None, slider=False):
    proxy_name = _izom_propui_free_editor_float_proxy_name(field_name, params)
    try:
        if text is None:
            layout.prop(item, proxy_name, slider=slider)
        else:
            layout.prop(item, proxy_name, text=text, slider=slider)
    except (AttributeError, TypeError, ValueError, ReferenceError):
        if text is None:
            layout.prop(item, field_name, slider=slider)
        else:
            layout.prop(item, field_name, text=text, slider=slider)


def _izom_propui_free_snap_dynamic_label_float_value_for_params(params, raw_value, *, base=0.0):
    decimals, step = _izom_propui_free_editor_float_settings(params)
    return _izom_propui_free_snap_editor_float_value(raw_value, decimals, step, base=base)


def _izom_propui_free_general_float_guard_key(item, field_name):
    return (str(field_name), _izom_propui_free_pointer_guard_key(item))


def _izom_propui_free_set_editor_float_setting_value(params, field_name, value):
    try:
        current_value = getattr(params, field_name)
    except AttributeError:
        current_value = None
    try:
        if isinstance(value, int):
            if int(current_value) != int(value):
                setattr(params, field_name, int(value))
        elif current_value is None or abs(float(current_value) - float(value)) > 1e-6:
            setattr(params, field_name, float(value))
    except (AttributeError, TypeError, ValueError):
        return


def _izom_propui_free_snap_entry_float_field(entry, params, field_name, *, base=0.0):
    guard_key = _izom_propui_free_general_float_guard_key(entry, field_name)
    if guard_key in _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD:
        return
    try:
        current_value = float(getattr(entry, field_name, 0.0))
    except (AttributeError, TypeError, ValueError):
        return
    snapped_value = _izom_propui_free_snap_editor_float_value_for_params(params, current_value, base=base)
    _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.add(guard_key)
    try:
        if abs(float(getattr(entry, field_name, 0.0)) - float(snapped_value)) > 1e-6:
            setattr(entry, field_name, float(snapped_value))
    finally:
        _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_general_float_field_updated(entry, context, *, field_name, base=0.0):
    guard_key = _izom_propui_free_general_float_guard_key(entry, field_name)
    if guard_key in _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD:
        return
    if _izom_propui_free_entry_field_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    try:
        current_value = float(getattr(entry, field_name, 0.0))
    except (AttributeError, TypeError, ValueError):
        return
    snapped_value = _izom_propui_free_snap_editor_float_value_for_params(params, current_value, base=base)
    _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.add(guard_key)
    try:
        if abs(float(getattr(entry, field_name, 0.0)) - float(snapped_value)) > 1e-6:
            setattr(entry, field_name, float(snapped_value))
    finally:
        _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.discard(guard_key)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)


def _izom_propui_free_entry_float_bounds(entry, params=None):
    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, None)
    min_value = _izom_propui_free_snap_editor_float_value_for_params(params, getattr(entry, 'min_float', 0.0), base=0.0)
    min_value = _izom_propui_free_clamp_float(min_value, default=0.0)
    max_value = _izom_propui_free_snap_editor_float_value_for_params(params, getattr(entry, 'max_float', min_value), base=0.0)
    max_value = _izom_propui_free_clamp_float(max_value, default=min_value)
    if max_value < min_value:
        max_value = min_value
    return min_value, max_value


def _izom_propui_free_entry_int_bounds(entry):
    min_value = _izom_propui_free_clamp_int(getattr(entry, 'min_int', 0), default=0)
    max_value = _izom_propui_free_clamp_int(getattr(entry, 'max_int', min_value), default=min_value)
    if max_value < min_value:
        max_value = min_value
    return min_value, max_value


def _izom_propui_free_clamp_entry_default_float(entry, params=None):
    guard_key = _izom_propui_free_general_float_guard_key(entry, 'default_float')
    if guard_key in _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD:
        return
    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, None)
    try:
        current_value = float(getattr(entry, 'default_float', 0.0))
    except (AttributeError, TypeError, ValueError):
        return
    min_value, max_value = _izom_propui_free_entry_float_bounds(entry, params)
    snapped_value = _izom_propui_free_snap_editor_float_value_for_params(params, current_value, base=0.0)
    clamped_value = _izom_propui_free_clamp_float(
        snapped_value,
        default=min_value,
        min_value=min_value,
        max_value=max_value,
    )
    _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.add(guard_key)
    try:
        if abs(float(getattr(entry, 'default_float', 0.0)) - float(clamped_value)) > 1e-6:
            entry.default_float = float(clamped_value)
    finally:
        _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_clamp_entry_default_int(entry):
    min_value, max_value = _izom_propui_free_entry_int_bounds(entry)
    clamped_value = _izom_propui_free_clamp_int(
        getattr(entry, 'default_int', min_value),
        default=min_value,
        min_value=min_value,
        max_value=max_value,
    )
    if int(getattr(entry, 'default_int', min_value)) != clamped_value:
        entry.default_int = clamped_value


def _izom_propui_free_range_guard_key(entry):
    return getattr(entry, 'uid', '') or str(entry.as_pointer())


def _izom_propui_free_float_range_updated(entry, _context):
    from .helper_value_labels_dependencies import _izom_propui_free_normalize_dependent_thresholds

    guard_key = _izom_propui_free_range_guard_key(entry)
    if guard_key in _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD:
        return
    if _izom_propui_free_entry_field_update_suspended(_context):
        return

    _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD.add(guard_key)
    try:
        params = _izom_propui_free_find_params_for_entry(entry, None)
        if _izom_propui_free_bulk_entry_updates_suspended(params):
            return
        min_value, max_value = _izom_propui_free_entry_float_bounds(entry, params)

        if float(getattr(entry, 'min_float', 0.0)) != min_value:
            entry.min_float = min_value
        if float(getattr(entry, 'max_float', min_value)) != max_value:
            entry.max_float = max_value

        soft_min = _izom_propui_free_snap_editor_float_value_for_params(params, getattr(entry, 'soft_min_float', min_value), base=0.0)
        soft_min = _izom_propui_free_clamp_float(soft_min, default=min_value, min_value=min_value, max_value=max_value)
        soft_max = _izom_propui_free_snap_editor_float_value_for_params(params, getattr(entry, 'soft_max_float', max_value), base=0.0)
        soft_max = _izom_propui_free_clamp_float(soft_max, default=max_value, min_value=soft_min, max_value=max_value)
        if soft_max < soft_min:
            soft_max = soft_min

        if float(getattr(entry, 'soft_min_float', min_value)) != soft_min:
            entry.soft_min_float = soft_min
        if float(getattr(entry, 'soft_max_float', max_value)) != soft_max:
            entry.soft_max_float = soft_max

        _izom_propui_free_clamp_entry_default_float(entry, params)
        _izom_propui_free_normalize_dependent_thresholds(entry, params)
    finally:
        _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD.discard(guard_key)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)


def _izom_propui_free_int_range_updated(entry, _context):
    from .helper_value_labels_dependencies import _izom_propui_free_normalize_dependent_thresholds

    guard_key = _izom_propui_free_range_guard_key(entry)
    if guard_key in _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD:
        return
    if _izom_propui_free_entry_field_update_suspended(_context):
        return

    _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD.add(guard_key)
    try:
        params = _izom_propui_free_find_params_for_entry(entry, None)
        if _izom_propui_free_bulk_entry_updates_suspended(params):
            return
        min_value, max_value = _izom_propui_free_entry_int_bounds(entry)

        if int(getattr(entry, 'min_int', 0)) != min_value:
            entry.min_int = min_value
        if int(getattr(entry, 'max_int', min_value)) != max_value:
            entry.max_int = max_value

        soft_min = _izom_propui_free_clamp_int(getattr(entry, 'soft_min_int', min_value), default=min_value, min_value=min_value, max_value=max_value)
        soft_max = _izom_propui_free_clamp_int(getattr(entry, 'soft_max_int', max_value), default=max_value, min_value=soft_min, max_value=max_value)
        if soft_max < soft_min:
            soft_max = soft_min

        if int(getattr(entry, 'soft_min_int', min_value)) != soft_min:
            entry.soft_min_int = soft_min
        if int(getattr(entry, 'soft_max_int', max_value)) != soft_max:
            entry.soft_max_int = soft_max

        _izom_propui_free_clamp_entry_default_int(entry)
        _izom_propui_free_normalize_dependent_thresholds(entry, params)
    finally:
        _IZOM_PROPUI_FREE_RANGE_UPDATE_GUARD.discard(guard_key)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_apply_editor_float_settings_to_entry(entry, params):
    from .helper_value_labels_thresholds import _izom_propui_free_normalize_value_label_collection

    _izom_propui_free_snap_entry_float_field(entry, params, 'default_float')
    _izom_propui_free_float_range_updated(entry, None)
    _izom_propui_free_snap_entry_float_field(entry, params, 'step_float')
    _izom_propui_free_snap_entry_float_field(entry, params, 'visibility_match_float')

    entry_prop_type = str(getattr(entry, 'prop_type', '') or '')
    if _izom_propui_free_is_numeric_type(entry_prop_type):
        _izom_propui_free_normalize_value_label_collection(entry, params=params)


def _izom_propui_free_apply_editor_float_settings(params):
    for entry in getattr(params, 'izom_propui_free_entries', []) or []:
        _izom_propui_free_apply_editor_float_settings_to_entry(entry, params)


def _izom_propui_free_ensure_editor_float_settings(params, *, apply_existing=False):
    guard_key = _izom_propui_free_pointer_guard_key(params)
    if guard_key in _IZOM_PROPUI_FREE_EDITOR_SETTINGS_UPDATE_GUARD:
        return _izom_propui_free_editor_float_settings(params)

    _IZOM_PROPUI_FREE_EDITOR_SETTINGS_UPDATE_GUARD.add(guard_key)
    try:
        decimals, _step = _izom_propui_free_editor_float_settings(params)
        changed = False
        try:
            if int(getattr(params, 'izom_propui_free_editor_float_decimals', decimals)) != int(decimals):
                changed = True
        except (AttributeError, TypeError, ValueError):
            changed = True
        _izom_propui_free_set_editor_float_setting_value(params, 'izom_propui_free_editor_float_decimals', decimals)
        if changed or apply_existing:
            _izom_propui_free_apply_editor_float_settings(params)
        return _izom_propui_free_editor_float_settings(params)
    finally:
        _IZOM_PROPUI_FREE_EDITOR_SETTINGS_UPDATE_GUARD.discard(guard_key)


def _izom_propui_free_editor_float_settings_updated(params, _context):
    _izom_propui_free_ensure_editor_float_settings(params, apply_existing=True)
    _izom_propui_free_invalidate_runtime_entry_cache(params)


def _izom_propui_free_editor_float_decimals_updated(params, context):
    _izom_propui_free_editor_float_settings_updated(params, context)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
